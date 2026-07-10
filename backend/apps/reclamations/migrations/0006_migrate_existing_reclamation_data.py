"""
Data migration: migrate existing Reclamation data to LigneReclamation.
This handles the case where Reclamation records already have note_elementaire,
note_originale, nouvelle_note, motif set before the fields were removed in 0005.
"""
from django.db import migrations


def migrate_existing_data(apps, schema_editor):
    Reclamation = apps.get_model('reclamations', 'Reclamation')
    LigneReclamation = apps.get_model('reclamations', 'LigneReclamation')

    for rec in Reclamation.objects.filter(
        note_elementaire__isnull=False,
    ).iterator():
        # Only create if no LigneReclamation exists for this reclamation yet
        if not LigneReclamation.objects.filter(reclamation=rec).exists():
            LigneReclamation.objects.create(
                reclamation=rec,
                note_elementaire=rec.note_elementaire,
                motif=rec.motif or 'AUTRE',
                note_originale=rec.note_originale,
                nouvelle_note=rec.nouvelle_note,
            )


def reverse_migration(apps, schema_editor):
    LigneReclamation = apps.get_model('reclamations', 'LigneReclamation')
    LigneReclamation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reclamations', '0005_create_lignereclamation'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_data, reverse_migration),
    ]