# Generated by Django 3.2.7 on 2021-09-27 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
