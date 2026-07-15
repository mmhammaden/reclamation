"""
Admin views for import, reporting, and academic year management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
import csv
from django.http import HttpResponse
from apps.notes.models import ResultatSemestre, ElementModule
from apps.users.models import User
from .models import AnneeAcademique
from .permissions import IsAdmin
from apps.notes.utils import (
    classify_column,
    extract_module_codes,
    parse_and_validate_file,
)


def _annee_to_dict(annee):
    return {
        'id': annee.id,
        'annee': annee.annee,
        'est_active': annee.est_active,
        'semestres_actifs': annee.semestres_actifs,
        'semestres_list': annee.get_semestres_list(),
        'date_creation': annee.date_creation.isoformat() if annee.date_creation else None,
    }


@api_view(['GET'])
@permission_classes([IsAdmin])
def annee_academique_current(request):
    """GET /api/admin/annee-academique/current/ — returns active year or 404."""
    try:
        annee = AnneeAcademique.objects.get(est_active=True)
        return Response(_annee_to_dict(annee))
    except AnneeAcademique.DoesNotExist:
        return Response({'detail': 'Aucune année académique active.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdmin])
def annee_academique_create(request):
    """POST /api/admin/annee-academique/ — create and activate a new academic year."""
    annee_str = request.data.get('annee', '').strip()
    semestres_actifs = request.data.get('semestres_actifs', '').strip()

    if not annee_str or not semestres_actifs:
        return Response(
            {'detail': 'Les champs annee et semestres_actifs sont obligatoires.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if AnneeAcademique.objects.filter(annee=annee_str).exists():
        return Response(
            {'detail': f"L'année {annee_str} existe déjà."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    annee = AnneeAcademique.objects.create(
        annee=annee_str,
        semestres_actifs=semestres_actifs,
        est_active=True,
    )
    return Response(_annee_to_dict(annee), status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def annee_academique_update(request, pk):
    """PATCH /api/admin/annee-academique/{id}/ — update semestres or toggle active."""
    try:
        annee = AnneeAcademique.objects.get(pk=pk)
    except AnneeAcademique.DoesNotExist:
        return Response({'detail': 'Année introuvable.'}, status=status.HTTP_404_NOT_FOUND)

    if 'semestres_actifs' in request.data:
        annee.semestres_actifs = request.data['semestres_actifs'].strip()
    if 'est_active' in request.data:
        annee.est_active = bool(request.data['est_active'])

    annee.save()
    return Response(_annee_to_dict(annee))


def process_row(row, semestre, annee_academique):
    """Process a single row: create/update student and resultat."""
    if isinstance(row, dict):
        matricule = row.get('Numéro', '').strip().upper()
        nom_prenom = row.get('Nom et Prénom', '').strip()
    else:
        matricule = str(row[0]).strip().upper() if row[0] else ''
        nom_prenom = str(row[1]).strip() if row[1] else ''

    if not matricule:
        raise ValueError("Matricule manquant")

    etudiant, created = User.objects.get_or_create(
        matricule=matricule,
        defaults={
            'email': f"{matricule.lower()}@iscae.edu.mr",
            'role': 'ETUDIANT',
        }
    )
    if created and nom_prenom:
        names = nom_prenom.split()
        if len(names) >= 2:
            etudiant.last_name = ' '.join(names[:-1])
            etudiant.first_name = names[-1]
        else:
            etudiant.last_name = nom_prenom
        etudiant.save()

    resultat, _ = ResultatSemestre.objects.update_or_create(
        etudiant=etudiant,
        semestre=semestre,
        annee_academique=annee_academique,
    )
    return etudiant, resultat


def process_element_data(row, resultat, module_codes):
    element_data = {}
    for col_name, value in row.items():
        if col_name in ['Numéro', 'Nom et Prénom', 'Moy. Semestre', 'Observation']:
            continue
        if col_name.endswith('_Nom'):
            ec = col_name[:-4]
            if ec not in element_data:
                element_data[ec] = {}
            element_data[ec]['nom_matiere'] = str(value).strip() if value else ''
            continue
        classification = classify_column(col_name, module_codes)
        if classification and classification.col_type == 'element':
            ec = classification.element_code
            if ec not in element_data:
                element_data[ec] = {}
            element_data[ec][classification.field] = value

    imported_count = 0
    for ec, edata in element_data.items():
        if 'Continu' not in edata and 'Final' not in edata:
            continue
        ElementModule.objects.update_or_create(
            resultat_semestre=resultat,
            code_element=ec,
            defaults={
                'nom_matiere': edata.get('nom_matiere', ''),
                'note_continu': float(edata.get('Continu', 0) or 0),
                'note_final': float(edata.get('Final', 0) or 0),
                'credit': float(edata.get('Credit', 0) or 0),
            }
        )
        imported_count += 1
    return imported_count


@api_view(['POST'])
@permission_classes([IsAdmin])
def import_pv(request):
    """
    POST /api/admin/import-pv/
    Admin: bulk import ResultatSemestre/ElementModule from CSV/XLSX file.
    Falls back to active academic year if semestre/annee_academique not provided.
    """
    fichier = request.FILES.get('fichier')
    if not fichier:
        return Response(
            {"detail": "Fichier requis."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fallback to active academic year if not provided
    active_annee = None
    try:
        active_annee = AnneeAcademique.objects.get(est_active=True)
    except AnneeAcademique.DoesNotExist:
        pass

    annee_academique = request.POST.get('annee_academique') or (active_annee.annee if active_annee else '2024-2025')
    semestre_default = active_annee.get_semestres_list()[0] if active_annee else 'S1'
    semestre = request.POST.get('semestre') or semestre_default

    imported_count = 0
    errors = []

    try:
        headers, rows = parse_and_validate_file(fichier)
        module_codes = extract_module_codes(headers)

        with transaction.atomic():
            for row in rows:
                try:
                    etudiant, resultat = process_row(row, semestre, annee_academique)
                    count = process_element_data(row, resultat, module_codes)
                    imported_count += count
                except Exception as e:
                    errors.append(f"Erreur sur ligne {row}: {str(e)}")

        return Response({
            "detail": f"Import terminé. {imported_count} élément(s) importé(s).",
            "imported": imported_count,
            "errors": errors[:50],
        })

    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"detail": f"Erreur lors de l'import: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAdmin])
def force_unblock_note(request, reclamation_id):
    """
    POST /api/admin/reclamations/{id}/force-unblock/
    RG-03: Admin can force-unblock a previously accepted element.
    """
    from .models import Reclamation, StatutReclamation, HistoriqueStatut

    try:
        reclamation = Reclamation.objects.get(id=reclamation_id)
    except Reclamation.DoesNotExist:
        return Response(
            {"detail": "Réclamation introuvable."},
            status=status.HTTP_404_NOT_FOUND
        )

    if reclamation.statut != StatutReclamation.ACCEPTEE:
        return Response(
            {"detail": "Seules les réclamations acceptées peuvent être débloquées."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        old_statut = reclamation.statut
        reclamation.statut = StatutReclamation.ARCHIVEE
        reclamation.save(update_fields=['statut'])

        HistoriqueStatut.objects.create(
            reclamation=reclamation,
            statut_precedent=old_statut,
            nouveau_statut=StatutReclamation.ARCHIVEE,
            commentaire="Déblocage forcé par l'administrateur (RG-03)",
            modifie_par=request.user,
        )

    return Response({
        "detail": f"Réclamation #{reclamation_id} débloquée.",
        "reclamation_id": reclamation.id,
        "nouveau_statut": StatutReclamation.ARCHIVEE,
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def export_rapport(request):
    """
    GET /api/rapports/?format=csv
    Admin: export reclamation statistics.
    """
    from .models import Reclamation

    format_type = request.query_params.get('format', 'csv')
    reclamations = Reclamation.objects.select_related(
        'etudiant', 'coordonnateur'
    ).prefetch_related('lignes', 'lignes__element_module').all()

    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rapport_reclamations.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Matricule', 'Étudiant', 'Élément', 'Type', 'Motif', 'Statut',
            'Date création', 'Date limite', 'Date traitement',
            'Note originale', 'Nouvelle note', 'Coordinateur', 'Commentaire'
        ])

        for r in reclamations:
            for l in r.lignes.all():
                writer.writerow([
                    r.id,
                    r.etudiant.matricule,
                    r.etudiant.get_full_name(),
                    l.element_module.code_element if l.element_module else '',
                    l.get_type_note_display(),
                    l.motif,
                    r.statut,
                    r.date_creation.strftime('%Y-%m-%d %H:%M'),
                    r.date_limite_traitement.strftime('%Y-%m-%d %H:%M'),
                    r.date_traitement.strftime('%Y-%m-%d %H:%M') if r.date_traitement else '',
                    l.note_originale,
                    l.nouvelle_note,
                    r.coordonnateur.get_full_name() if r.coordonnateur else '',
                    r.commentaire_decision,
                ])

        return response

    return Response({"detail": "Format non supporté. Utilisez ?format=csv"})