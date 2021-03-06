# Generated by Django 3.2.7 on 2021-09-26 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_alter_contract_client'),
        ('events', '0002_alter_event_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='contract',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='clients.contract'),
        ),
    ]
