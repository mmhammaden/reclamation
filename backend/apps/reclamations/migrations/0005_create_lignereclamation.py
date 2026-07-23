# Generated migration for LigneReclamation model (create only, no RemoveField)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0004_hierarchical_structure'),
        ('reclamations', '0004_reclamation_commentaire_professeur_and_more'),
    ]

    operations = [
        # Créer LigneReclamation (keep old fields for data migration)
        migrations.CreateModel(
            name='LigneReclamation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motif', models.CharField(choices=[
                    ('ERREUR_SAISIE', 'Erreur de saisie'),
                    ('OUBLI_NOTE', 'Oubli de note'),
                    ('VERIFICATION_COPIE', 'Demande de vérification de copie'),
                    ('AUTRE', 'Autre motif'),
                ], max_length=30)),
                ('note_originale', models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)),
                ('nouvelle_note', models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)),
                ('reclamation', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='lignes',
                    to='reclamations.reclamation',
                )),
                ('element_module', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    related_name='lignes_reclamation',
                    to='notes.elementmodule',
                )),
            ],
            options={
                'verbose_name': 'Ligne de réclamation',
                'verbose_name_plural': 'Lignes de réclamation',
                'unique_together': {('reclamation', 'element_module')},
            },
        ),
    ]
