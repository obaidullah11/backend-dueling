# Generated by Django 5.0 on 2024-11-08 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fixture',
            name='is_tournament_completed',
        ),
    ]
