# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-07 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20161206_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicegroup',
            name='friendly_name',
            field=models.CharField(default='', max_length=500),
        ),
    ]
