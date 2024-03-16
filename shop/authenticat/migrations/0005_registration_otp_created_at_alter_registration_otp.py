# Generated by Django 5.0.3 on 2024-03-16 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticat', '0004_registration_vendor_application_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='otp',
            field=models.CharField(default='000', max_length=6, null=True),
        ),
    ]