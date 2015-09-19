# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child_name', models.CharField(max_length=200, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('is_on', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WeMoSwitch',
            fields=[
                ('switch_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='power.Switch')),
                ('device_name', models.CharField(max_length=255)),
                ('device_ip', models.CharField(max_length=255)),
                ('device_mac', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('power.switch',),
        ),
        migrations.AddField(
            model_name='switch',
            name='home',
            field=models.ForeignKey(blank=True, to='core.Home', null=True),
        ),
        migrations.AddField(
            model_name='switch',
            name='room',
            field=models.ForeignKey(blank=True, to='core.Room', null=True),
        ),
    ]
