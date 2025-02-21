# Generated by Django 5.0.6 on 2025-02-21 08:48

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
            name='Affiliate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referral_code', models.CharField(blank=True, max_length=20, unique=True)),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Active', 'Active'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='Pending', max_length=10)),
                ('commission_rate', models.FloatField(default=5.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='affiliate_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referral_code', models.CharField(blank=True, max_length=20, unique=True)),
                ('referral_link', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Joined', 'Joined'), ('Completed', 'Completed'), ('Canceled', 'Canceled')], default='Pending', max_length=10)),
                ('clicks', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referred_by', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='affiliates.affiliate')),
            ],
        ),
    ]
