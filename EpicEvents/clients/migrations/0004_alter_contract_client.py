# Generated by Django 3.2.7 on 2021-09-26 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_auto_20210922_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='client',
            field=models.ForeignKey(limit_choices_to=models.Q(('sales_contact__isnull', False)), on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='clients.client'),
        ),
    ]
