# Generated by Django 2.0.7 on 2018-09-24 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DihedralAngle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='Двугранный угол')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.Document')),
            ],
        ),
        migrations.CreateModel(
            name='DihedralAngleLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('angle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.DihedralAngle')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.Link')),
            ],
        ),
        migrations.CreateModel(
            name='ValenceAngle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='Валентный угол')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.Document')),
            ],
        ),
        migrations.CreateModel(
            name='ValenceAngleLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('angle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.ValenceAngle')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='editor.Link')),
            ],
        ),
    ]