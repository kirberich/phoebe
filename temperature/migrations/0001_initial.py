# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemperatureController',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child_name', models.CharField(max_length=200, null=True, blank=True)),
                ('normal_temperature', models.FloatField(default=22)),
                ('away_temperature', models.FloatField(default=18)),
                ('vacation_temperature', models.FloatField(default=15)),
                ('warm_temperature', models.FloatField(default=23)),
                ('hot_temperature', models.FloatField(default=25)),
                ('last_target_temperature', models.FloatField(default=0)),
                ('target_temperature', models.FloatField(default=0)),
                ('current_temperature', models.FloatField(default=0)),
                ('is_in_vacation_mode', models.BooleanField(default=False)),
                ('is_in_away_mode', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('auto_away', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Nest',
            fields=[
                ('temperaturecontroller_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='temperature.TemperatureController')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('structure_name', models.CharField(max_length=255, blank=True)),
                ('device_name', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('temperature.temperaturecontroller',),
        ),
        migrations.AddField(
            model_name='temperaturecontroller',
            name='home',
            field=models.ForeignKey(to='core.Home'),
        ),
        migrations.AddField(
            model_name='temperaturecontroller',
            name='room',
            field=models.ForeignKey(to='core.Room'),
        ),
    ]
