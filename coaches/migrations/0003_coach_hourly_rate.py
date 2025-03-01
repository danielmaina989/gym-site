# Generated by Django 5.0.6 on 2025-01-27 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coaches', '0002_coach_workout_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='coach',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Hourly rate of the coach', max_digits=6),
        ),
    ]
