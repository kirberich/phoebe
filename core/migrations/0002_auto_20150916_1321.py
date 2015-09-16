# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='home',
            field=models.ForeignKey(related_name='devices', to='core.Home'),
        ),
    ]
