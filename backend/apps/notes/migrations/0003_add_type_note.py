# Generated migration for adding type_note field to NoteElementaire

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='noteelementaire',
            name='type_note',
            field=models.CharField(
                choices=[('DEVOIR', 'Devoir'), ('EXAMEN', 'Examen')],
                default='DEVOIR',
                max_length=10,
                verbose_name='Type de note',
                help_text='Devoir ou Examen',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='noteelementaire',
            unique_together={('etudiant', 'code_module', 'type_note', 'semestre', 'annee_academique')},
        ),
    ]