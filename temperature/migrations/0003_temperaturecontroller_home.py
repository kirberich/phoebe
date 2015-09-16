# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('temperature', '0002_temperaturecontroller_auto_away'),
    ]

    operations = [
        migrations.AddField(
            model_name='temperaturecontroller',
            name='home',
            field=models.ForeignKey(default=1, to='core.Home'),
            preserve_default=False,
        ),
    ]
