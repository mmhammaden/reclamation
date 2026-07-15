# Generated migration for flattened structure: ResultatSemestre → ElementModule
# Removes Module model, adds resultat_semestre FK directly on ElementModule

from django.db import migrations, models
import django.db.models.deletion


def migrate_elementmodule_to_resultat(apps, schema_editor):
    """
    Migrate existing ElementModule data to use resultat_semestre FK.
    This populates the new FK from the module's resultat_semestre.
    """
    ElementModule = apps.get_model('notes', 'ElementModule')
    db_alias = schema_editor.connection.alias
    
    # Update all ElementModule records to set resultat_semestre from their module
    for element in ElementModule.objects.using(db_alias).all():
        if element.module_id:
            element.resultat_semestre = element.module.resultat_semestre
            element.save(update_fields=['resultat_semestre'])


def reverse_migrate_resultat_to_module(apps, schema_editor):
    """
    Reverse migration: restore module FK from resultat_semestre.
    
    Note: This is a best-effort reverse. The original Module records are deleted
    in the forward migration, so we cannot perfectly restore them. We create new
    Module records based on element codes (e.g., MIAG311 -> MIAG31) with default values.
    
    For a proper rollback, you would need to re-import the PV data.
    """
    ElementModule = apps.get_model('notes', 'ElementModule')
    Module = apps.get_model('notes', 'Module')
    db_alias = schema_editor.connection.alias
    
    # Group elements by resultat_semestre to recreate modules
    from collections import defaultdict
    elements_by_resultat = defaultdict(list)
    
    for element in ElementModule.objects.using(db_alias).all():
        if element.resultat_semestre_id:
            elements_by_resultat[element.resultat_semestre_id].append(element)
    
    # For each resultat, create a module and assign elements to it
    for resultat_id, elements in elements_by_resultat.items():
        if elements:
            # Extract module code from first element (e.g., MIAG311 -> MIAG31)
            first_code = elements[0].code_element
            # Module code is typically first 5 chars (e.g., MIAG31 from MIAG311)
            module_code = first_code[:5] if len(first_code) >= 5 else first_code
            
            # Get or create module for this resultat
            module, _ = Module.objects.using(db_alias).get_or_create(
                resultat_semestre_id=resultat_id,
                code_module=module_code,
                defaults={
                    'nom_module': f'Module {module_code}',
                    'moy_module': 0,
                    'note_finale': 0,
                    'credit': 0,
                    'observation': 'Rattrapage',
                }
            )
            
            # Assign elements to the module
            for element in elements:
                element.module = module
                element.save(update_fields=['module'])


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0006_add_nom_element'),
    ]

    operations = [
        # Clear unique_together BEFORE removing the module field
        migrations.AlterUniqueTogether(
            name='elementmodule',
            unique_together=set(),
        ),
        # Add resultat_semestre FK to ElementModule (nullable first)
        migrations.AddField(
            model_name='elementmodule',
            name='resultat_semestre',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='elements',
                to='notes.resultatsemestre',
                verbose_name="Résultat de semestre",
                null=True,
                blank=True,
            ),
        ),
        # Migrate data: populate resultat_semestre from module
        migrations.RunPython(
            migrate_elementmodule_to_resultat,
            reverse_migrate_resultat_to_module,
        ),
        # Now make the field non-nullable
        migrations.AlterField(
            model_name='elementmodule',
            name='resultat_semestre',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='elements',
                to='notes.resultatsemestre',
                verbose_name="Résultat de semestre",
            ),
        ),
        # Remove the Module model
        migrations.RemoveField(
            model_name='elementmodule',
            name='module',
        ),
        migrations.DeleteModel(
            name='Module',
        ),
        # Rename nom_element to nom_matiere
        migrations.RenameField(
            model_name='elementmodule',
            old_name='nom_element',
            new_name='nom_matiere',
        ),
    ]
