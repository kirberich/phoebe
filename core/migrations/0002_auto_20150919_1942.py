# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='home',
            name='notification_settings',
        ),
        migrations.AddField(
            model_name='user',
            name='api_key',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
