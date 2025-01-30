# Generated by Django 5.0.6 on 2025-01-29 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_booking_created_at_booking_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='training_time',
            field=models.CharField(choices=[('08:00', '08:00'), ('10:00', '10:00'), ('13:30', '13:30'), ('16:00', '16:00')], default='08:00', max_length=5),
        ),
    ]
