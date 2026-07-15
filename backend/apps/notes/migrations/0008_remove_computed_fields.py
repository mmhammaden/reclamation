# Remove computed fields that are now @property methods
# - ElementModule: note_moyenne, observation
# - ResultatSemestre: moy_semestre, observation

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_flattened_structure'),
    ]

    operations = [
        # Remove computed fields from ElementModule
        migrations.RemoveField(
            model_name='elementmodule',
            name='note_moyenne',
        ),
        migrations.RemoveField(
            model_name='elementmodule',
            name='observation',
        ),
        # Remove computed fields from ResultatSemestre
        migrations.RemoveField(
            model_name='resultatsemestre',
            name='moy_semestre',
        ),
        migrations.RemoveField(
            model_name='resultatsemestre',
            name='observation',
        ),
    ]