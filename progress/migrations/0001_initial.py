# Generated by Django 5.2 on 2025-04-06 03:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('weight', models.FloatField(help_text='Peso atual em kg')),
                ('body_fat', models.FloatField(blank=True, help_text='Percentual de gordura corporal', null=True)),
                ('muscle_mass', models.FloatField(blank=True, help_text='Massa muscular em kg (opcional)', null=True)),
                ('waist_circumference', models.FloatField(blank=True, help_text='Circunferência da cintura em cm', null=True)),
                ('hip_circumference', models.FloatField(blank=True, help_text='Circunferência do quadril em cm', null=True)),
                ('chest_circumference', models.FloatField(blank=True, help_text='Circunferência do tórax em cm', null=True)),
                ('notes', models.TextField(blank=True, help_text='Anotações adicionais sobre o progresso')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
