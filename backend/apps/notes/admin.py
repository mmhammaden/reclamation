import csv
from django.contrib import admin
from django.db import transaction
from django.contrib import messages
from .models import ResultatSemestre, Module, ElementModule


# Known module-level column suffixes (exact match after module code)
MODULE_COL_SUFFIXES = {'_Moy_Module', '_Note_Finale', '_Credit', '_Observation'}
# Known element-level column suffixes
ELEMENT_COL_SUFFIXES = {'_Continu', '_Final', '_Note', '_Credit', '_Obs'}


def classify_column(col_name, module_codes):
    """
    Classify a column as module-level or element-level.
    Returns ('module', module_code, field) or ('element', module_code, element_code, field) or None.
    """
    for suffix in MODULE_COL_SUFFIXES:
        if col_name.endswith(suffix):
            module_code = col_name[:-len(suffix)]
            if module_code in module_codes:
                field = suffix[1:]  # Remove leading underscore
                return ('module', module_code, field)

    for suffix in ELEMENT_COL_SUFFIXES:
        if col_name.endswith(suffix):
            element_code = col_name[:-len(suffix)]
            # Check if this element_code starts with any known module code
            for mc in module_codes:
                if element_code.startswith(mc) and len(element_code) > len(mc):
                    return ('element', mc, element_code, suffix[1:])

    return None


def extract_module_codes(headers):
    """Extract module codes from column headers."""
    codes = set()
    for col in headers:
        for suffix in MODULE_COL_SUFFIXES:
            if col.endswith(suffix):
                codes.add(col[:-len(suffix)])
    return codes


class ElementModuleInline(admin.TabularInline):
    model = ElementModule
    extra = 0
    readonly_fields = ('code_element', 'note_continu', 'note_final', 'note_moyenne', 'credit', 'observation')
    can_delete = False


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    readonly_fields = ('code_module', 'moy_module', 'note_finale', 'credit', 'observation')
    can_delete = False


@admin.register(ResultatSemestre)
class ResultatSemestreAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'moy_semestre', 'observation', 'semestre', 'annee_academique')
    list_filter = ('annee_academique', 'semestre', 'observation')
    search_fields = ('etudiant__matricule', 'etudiant__email')
    inlines = [ModuleInline]
    actions = ['import_pv_action']

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
        from apps.users.models import User

        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            semestre = request.POST.get('semestre', 'S3')
            annee_academique = request.POST.get('annee_academique', '2024-2025')

            if not csv_file:
                self.message_user(request, "Aucun fichier CSV sélectionné.", messages.ERROR)
                return redirect('..')

            try:
                with transaction.atomic():
                    content = csv_file.read().decode('utf-8-sig').splitlines()
                    reader = csv.DictReader(content)
                    headers = reader.fieldnames if reader.fieldnames else []

                    # Extract module codes from headers
                    module_codes = extract_module_codes(headers)

                    imported_count = 0
                    errors = []

                    for row in reader:
                        try:
                            # Get or create student
                            matricule = row.get('Numéro', '').strip()
                            nom_prenom = row.get('Nom et Prénom', '').strip()
                            moy_semestre = row.get('Moy. Semestre', '0').strip()
                            observation = row.get('Observation', 'Rattrapage').strip()

                            if not matricule:
                                errors.append(f"Ligne invalide: matricule manquant")
                                continue

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

                            # Create/update ResultatSemestre
                            resultat, _ = ResultatSemestre.objects.update_or_create(
                                etudiant=user,
                                semestre=semestre,
                                annee_academique=annee_academique,
                                defaults={
                                    'moy_semestre': float(moy_semestre) if moy_semestre else 0,
                                    'observation': observation,
                                }
                            )

                            # First pass: collect module-level data
                            module_data = {}
                            for col_name, value in row.items():
                                if col_name in ['Numéro', 'Nom et Prénom', 'Moy. Semestre', 'Observation']:
                                    continue

                                classification = classify_column(col_name, module_codes)
                                if classification and classification[0] == 'module':
                                    _, mc, field = classification
                                    if mc not in module_data:
                                        module_data[mc] = {}
                                    module_data[mc][field] = value

                            # Second pass: collect element-level data per module
                            element_data = {}
                            for col_name, value in row.items():
                                if col_name in ['Numéro', 'Nom et Prénom', 'Moy. Semestre', 'Observation']:
                                    continue

                                classification = classify_column(col_name, module_codes)
                                if classification and classification[0] == 'element':
                                    _, mc, ec, field = classification
                                    key = (mc, ec)
                                    if key not in element_data:
                                        element_data[key] = {}
                                    element_data[key][field] = value

                            # Create/update modules
                            for mc, mdata in module_data.items():
                                module, _ = Module.objects.update_or_create(
                                    resultat_semestre=resultat,
                                    code_module=mc,
                                    defaults={
                                        'moy_module': float(mdata.get('moy_module', 0) or 0),
                                        'note_finale': float(mdata.get('note_finale', 0) or 0),
                                        'credit': float(mdata.get('credit', 0) or 0),
                                        'observation': mdata.get('observation', 'Rattrapage'),
                                    }
                                )

                                # Create/update elements for this module
                                for (mc_key, ec), edata in element_data.items():
                                    if mc_key != mc:
                                        continue

                                    ElementModule.objects.update_or_create(
                                        module=module,
                                        code_element=ec,
                                        defaults={
                                            'note_continu': float(edata.get('Continu', 0) or 0),
                                            'note_final': float(edata.get('Final', 0) or 0),
                                            'note_moyenne': float(edata.get('Note', 0) or 0),
                                            'credit': float(edata.get('Credit', 0) or 0),
                                            'observation': edata.get('Obs', 'Rattrapage'),
                                        }
                                    )
                                    imported_count += 1

                        except Exception as e:
                            errors.append(f"Erreur sur ligne {row}: {str(e)}")

                    if errors:
                        self.message_user(request, f"Importation terminée avec {len(errors)} erreur(s).", messages.WARNING)
                    else:
                        self.message_user(request, f"Importation réussie depuis {csv_file.name}. {imported_count} élément(s) importé(s).", messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"Erreur lors de l'import: {str(e)}", messages.ERROR)

            return redirect('..')

        return render(request, 'admin/import_pv.html', {
            'title': 'Importer un PV',
            'opts': self.model._meta,
        })


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code_module', 'moy_module', 'note_finale', 'credit', 'observation', 'resultat_semestre')
    list_filter = ('code_module', 'observation', 'resultat_semestre__semestre')
    search_fields = ('code_module', 'resultat_semestre__etudiant__matricule')
    inlines = [ElementModuleInline]
    readonly_fields = ('code_module', 'moy_module', 'note_finale', 'credit', 'observation')


@admin.register(ElementModule)
class ElementModuleAdmin(admin.ModelAdmin):
    list_display = ('code_element', 'note_continu', 'note_final', 'note_moyenne', 'credit', 'observation', 'module')
    list_filter = ('observation', 'module__code_module', 'module__resultat_semestre__semestre')
    search_fields = ('code_element', 'module__resultat_semestre__etudiant__matricule')
    readonly_fields = ('code_element', 'note_continu', 'note_final', 'note_moyenne', 'credit', 'observation')