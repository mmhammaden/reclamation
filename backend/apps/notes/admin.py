import csv
from django.contrib import admin
from django.db import transaction
from django.contrib import messages
from .models import ResultatSemestre, ElementModule
from .utils import (
    classify_column,
    extract_module_codes,
    parse_and_validate_file,
)


class ElementModuleInline(admin.TabularInline):
    model = ElementModule
    extra = 0
    readonly_fields = ('code_element', 'nom_matiere', 'note_continu', 'note_final', 'get_note_moyenne', 'credit', 'get_observation')
    can_delete = False

    def get_note_moyenne(self, obj):
        return obj.note_moyenne
    get_note_moyenne.short_description = 'Note Moyenne'

    def get_observation(self, obj):
        return obj.observation
    get_observation.short_description = 'Observation'


def save_student_and_resultat(row, semestre, annee_academique):
    """
    Create or update student and ResultatSemestre from a row.
    Returns (user, resultat, errors) tuple.
    """
    from apps.users.models import User
    
    errors = []
    matricule = row.get('Numéro', '').strip().upper()
    nom_prenom = row.get('Nom et Prénom', '').strip()

    if not matricule:
        errors.append("Ligne invalide: matricule manquant")
        return None, None, errors

    user, created = User.objects.get_or_create(
        matricule=matricule,
        defaults={
            'email': f"{matricule.lower()}@iscae.edu.mr",
            'role': 'ETUDIANT',
        }
    )
    if created and nom_prenom:
        names = nom_prenom.split()
        if len(names) >= 2:
            user.last_name = ' '.join(names[:-1])
            user.first_name = names[-1]
        else:
            user.last_name = nom_prenom
        user.save()

    # Create/update ResultatSemestre (moy_semestre and observation are computed)
    resultat, _ = ResultatSemestre.objects.update_or_create(
        etudiant=user,
        semestre=semestre,
        annee_academique=annee_academique,
    )
    
    return user, resultat, errors


def save_element_modules(resultat, row, module_codes):
    element_data = {}
    for col_name, value in row.items():
        if col_name in ['Numéro', 'Nom et Prénom', 'Moy. Semestre', 'Observation']:
            continue

        # Handle _Nom columns directly
        if col_name.endswith('_Nom'):
            ec = col_name[:-4]  # strip "_Nom"
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
        # Only process elements that have numeric data (skip module-level _Nom entries)
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


@admin.register(ResultatSemestre)
class ResultatSemestreAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'get_moy_semestre', 'get_observation', 'semestre', 'annee_academique')
    list_filter = ('annee_academique', 'semestre')
    search_fields = ('etudiant__matricule', 'etudiant__email')
    inlines = [ElementModuleInline]
    actions = ['import_pv_action']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('elements')

    def get_moy_semestre(self, obj):
        return obj.moy_semestre
    get_moy_semestre.short_description = 'Moyenne'
    get_moy_semestre.admin_order_field = 'id'  # Can't order by computed field

    def get_observation(self, obj):
        return obj.observation
    get_observation.short_description = 'Observation'

    def import_pv_action(self, request, queryset):
        pass  # Placeholder - actual import via custom view
    import_pv_action.short_description = "Importer un PV (CSV)"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-pv/', self.admin_site.admin_view(self.import_pv_view), name='notes-resultatsemestre-import-pv'),
        ]
        return custom_urls + urls

    def import_pv_view(self, request):
        from django.shortcuts import render, redirect

        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            semestre = request.POST.get('semestre', 'S3')
            annee_academique = request.POST.get('annee_academique', '2024-2025')

            if not csv_file:
                self.message_user(request, "Aucun fichier CSV sélectionné.", messages.ERROR)
                return redirect('..')

            try:
                with transaction.atomic():
                    headers, rows = parse_and_validate_file(csv_file)

                    # Extract module codes from headers
                    module_codes = extract_module_codes(headers)

                    imported_count = 0
                    errors = []

                    for row in rows:
                        try:
                            user, resultat, row_errors = save_student_and_resultat(row, semestre, annee_academique)
                            if row_errors:
                                errors.extend(row_errors)
                                continue

                            count = save_element_modules(resultat, row, module_codes)
                            imported_count += count

                        except Exception as e:
                            errors.append(f"Erreur sur ligne {row}: {str(e)}")

                    if errors:
                        self.message_user(request, f"Importation terminée avec {len(errors)} erreur(s).", messages.WARNING)
                    else:
                        self.message_user(request, f"Importation réussie depuis {csv_file.name}. {imported_count} élément(s) importé(s).", messages.SUCCESS)

            except ValueError as e:
                self.message_user(request, str(e), messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Erreur lors de l'import: {str(e)}", messages.ERROR)

            return redirect('..')

        return render(request, 'admin/import_pv.html', {
            'title': 'Importer un PV',
            'opts': self.model._meta,
        })


@admin.register(ElementModule)
class ElementModuleAdmin(admin.ModelAdmin):
    list_display = ('code_element', 'nom_matiere', 'note_continu', 'note_final', 'get_note_moyenne', 'credit', 'get_observation', 'resultat_semestre')
    list_filter = ('resultat_semestre__semestre',)
    search_fields = ('code_element', 'nom_matiere', 'resultat_semestre__etudiant__matricule')
    readonly_fields = ('code_element', 'nom_matiere', 'note_continu', 'note_final', 'get_note_moyenne', 'credit', 'get_observation')

    def get_note_moyenne(self, obj):
        return obj.note_moyenne
    get_note_moyenne.short_description = 'Note Moyenne'

    def get_observation(self, obj):
        return obj.observation
    get_observation.short_description = 'Observation'