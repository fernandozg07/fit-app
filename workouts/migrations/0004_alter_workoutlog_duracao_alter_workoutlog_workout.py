# Generated by Django 5.2 on 2025-04-11 00:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0003_remove_workoutfeedback_feedback_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workoutlog',
            name='duracao',
            field=models.IntegerField(help_text='Duração do treino em minutos'),
        ),
        migrations.AlterField(
            model_name='workoutlog',
            name='workout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='workouts.workout'),
        ),
    ]
