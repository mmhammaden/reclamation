# Remove old fields from Reclamation (after data migration in 0006)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reclamations', '0006_migrate_existing_reclamation_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reclamation',
            name='note_elementaire',
        ),
        migrations.RemoveField(
            model_name='reclamation',
            name='note_originale',
        ),
        migrations.RemoveField(
            model_name='reclamation',
            name='nouvelle_note',
        ),
        migrations.RemoveField(
            model_name='reclamation',
            name='motif',
        ),
    ]