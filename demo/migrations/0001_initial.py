# Generated by Django 3.0.2 on 2020-01-06 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DemoStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jsonAtoms', models.TextField(default='[{"label": "H1", "color": 13238320, "x": 0, "y": 0, "z": 0}]')),
            ],
        ),
    ]
