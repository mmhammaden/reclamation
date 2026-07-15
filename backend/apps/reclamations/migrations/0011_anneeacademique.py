from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reclamations', '0010_hierarchical_structure'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnneeAcademique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee', models.CharField(max_length=20, unique=True)),
                ('est_active', models.BooleanField(default=False)),
                ('semestres_actifs', models.CharField(max_length=50)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Année académique',
                'verbose_name_plural': 'Années académiques',
                'ordering': ['-annee'],
            },
        ),
    ]