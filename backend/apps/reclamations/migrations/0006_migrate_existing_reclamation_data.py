"""
Data migration: No-op since note_elementaire field was removed from Reclamation.
The LigneReclamation model now uses element_module directly.
"""
from django.db import migrations


def migrate_existing_data(apps, schema_editor):
    # No-op: note_elementaire field no longer exists on Reclamation
    pass


def reverse_migration(apps, schema_editor):
    # No-op: nothing to reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reclamations', '0005_create_lignereclamation'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_data, reverse_migration),
    ]
