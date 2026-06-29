"""
Admin views for import and reporting.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
import openpyxl
import csv
import io
from apps.notes.models import NoteElementaire
from apps.users.models import User
from .permissions import IsAdmin


@api_view(['POST'])
@permission_classes([IsAdmin])
def import_pv(request):
    """
    POST /api/admin/import-pv/
    Admin: bulk import NoteElementaire from CSV/XLSX file.
    Expected columns: matricule, code_module, nom_module, semestre,
                      annee_academique, valeur_note, coefficient
    """
    fichier = request.FILES.get('fichier')
    if not fichier:
        return Response(
            {"detail": "Fichier requis."},
            status=status.HTTP_400_BAD_REQUEST
        )

    imported_count = 0
    errors = []

    try:
        if fichier.name.endswith('.xlsx'):
            wb = openpyxl.load_workbook(fichier)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=2, values_only=True))
            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        elif fichier.name.endswith('.csv'):
            decoded = fichier.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            rows = []
            for row in reader:
                rows.append((
                    row.get('matricule'),
                    row.get('code_module'),
                    row.get('nom_module'),
                    row.get('semestre'),
                    row.get('annee_academique'),
                    row.get('valeur_note'),
                    row.get('coefficient', 1.0),
                ))
            headers = list(reader.fieldnames) if reader.fieldnames else []
        else:
            return Response(
                {"detail": "Format non supporté. Utilisez CSV ou XLSX."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for row in rows:
                try:
                    matricule, code_module, nom_module, semestre, annee_acad, valeur, coeff = row[:7]

                    if not all([matricule, code_module, semestre, annee_acad, valeur]):
                        errors.append(f"Ligne invalide: {row}")
                        continue

                    try:
                        etudiant = User.objects.get(matricule=str(matricule).strip(), role='ETUDIANT')
                    except User.DoesNotExist:
                        errors.append(f"Étudiant {matricule} introuvable")
                        continue

                    NoteElementaire.objects.update_or_create(
                        etudiant=etudiant,
                        code_module=str(code_module).strip(),
                        semestre=str(semestre).strip(),
                        annee_academique=str(annee_acad).strip(),
                        defaults={
                            'nom_module': str(nom_module).strip() if nom_module else '',
                            'valeur_note': float(valeur),
                            'coefficient': float(coeff) if coeff else 1.0,
                        }
                    )
                    imported_count += 1

                except Exception as e:
                    errors.append(f"Erreur sur ligne {row}: {str(e)}")

        return Response({
            "detail": f"Import terminé. {imported_count} note(s) importée(s).",
            "imported": imported_count,
            "errors": errors[:50],  # Limit error messages
        })

    except Exception as e:
        return Response(
            {"detail": f"Erreur lors de l'import: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAdmin])
def export_rapport(request):
    """
    GET /api/rapports/?format=csv
    Admin: export reclamation statistics.
    """
    from .models import Reclamation
    from django.http import HttpResponse
    import csv

    format_type = request.query_params.get('format', 'csv')

    reclamations = Reclamation.objects.select_related(
        'etudiant', 'note_elementaire', 'coordonnateur'
    ).all()

    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rapport_reclamations.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Matricule', 'Étudiant', 'Module', 'Motif', 'Statut',
            'Date création', 'Date limite', 'Date traitement',
            'Note originale', 'Nouvelle note', 'Coordinateur', 'Commentaire'
        ])

        for r in reclamations:
            writer.writerow([
                r.id,
                r.etudiant.matricule,
                r.etudiant.get_full_name(),
                r.note_elementaire.code_module if r.note_elementaire else '',
                r.motif,
                r.statut,
                r.date_creation.strftime('%Y-%m-%d %H:%M'),
                r.date_limite_traitement.strftime('%Y-%m-%d %H:%M'),
                r.date_traitement.strftime('%Y-%m-%d %H:%M') if r.date_traitement else '',
                r.note_originale,
                r.nouvelle_note,
                r.coordonnateur.get_full_name() if r.coordonnateur else '',
                r.commentaire_decision,
            ])

        return response

    return Response({"detail": "Format non supporté. Utilisez ?format=csv"})