# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='node_position',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
