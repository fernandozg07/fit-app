# Generated by Django 5.2 on 2025-04-06 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='progressentry',
            options={},
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='body_fat',
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='chest_circumference',
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='hip_circumference',
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='muscle_mass',
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='progressentry',
            name='waist_circumference',
        ),
        migrations.AddField(
            model_name='progressentry',
            name='body_fat_percentage',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='progressentry',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='progressentry',
            name='weight',
            field=models.FloatField(),
        ),
    ]
