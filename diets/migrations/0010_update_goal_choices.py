# Generated manually to fix GOAL_CHOICES

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0009_alter_consumedmeallog_carbs_consumed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diet',
            name='goal',
            field=models.CharField(blank=True, choices=[('perda_peso', 'Perda de peso'), ('ganho_massa', 'Ganho de massa'), ('manutencao', 'Manutenção'), ('definicao', 'Definição')], help_text='Objetivo do plano.', max_length=50, null=True),
        ),
    ]