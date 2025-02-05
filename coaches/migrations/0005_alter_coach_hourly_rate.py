# Generated by Django 5.0.6 on 2025-02-05 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coaches', '0004_coach_resume_alter_coach_hourly_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coach',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]
