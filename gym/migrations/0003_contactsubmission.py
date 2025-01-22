# Generated by Django 5.0.6 on 2025-01-22 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0002_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('enquiry_type', models.CharField(choices=[('enquiry', 'Enquiry'), ('complaint', 'Complaint'), ('feedback', 'Feedback')], default='enquiry', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
