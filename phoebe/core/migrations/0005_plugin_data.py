# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-21 19:33
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20170817_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
