# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('power', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='auto_off',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='switch',
            name='auto_on',
            field=models.BooleanField(default=False),
        ),
    ]
