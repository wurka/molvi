# Generated by Django 2.1rc1 on 2019-09-21 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='atom',
            name='mentableindex',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='atom',
            name='valence',
            field=models.FloatField(default=1),
        ),
    ]
