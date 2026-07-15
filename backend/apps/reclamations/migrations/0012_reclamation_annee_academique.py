import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reclamations', '0011_anneeacademique'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamation',
            name='annee_academique',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reclamations',
                to='reclamations.anneeacademique',
            ),
        ),
        migrations.AddIndex(
            model_name='reclamation',
            index=models.Index(fields=['annee_academique'], name='reclamations_annee_academique_idx'),
        ),
    ]