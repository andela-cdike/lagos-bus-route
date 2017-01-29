# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-27 17:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('busstops', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_last_modified', models.DateField(auto_now=True)),
                ('busstop_type', models.CharField(choices=[('TE', 'Terminal'), ('TR', 'Transit')], default='TE', max_length=2)),
                ('route_id', models.IntegerField()),
                ('busstop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busstops.BusStop')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]