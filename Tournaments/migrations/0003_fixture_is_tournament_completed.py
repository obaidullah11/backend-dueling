# Generated by Django 5.0 on 2024-11-08 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tournaments', '0002_remove_fixture_is_tournament_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixture',
            name='is_tournament_completed',
            field=models.BooleanField(default=False),
        ),
    ]
