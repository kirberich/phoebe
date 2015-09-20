# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings
import dirtyfields.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name=b'email address')),
                ('nickname', models.CharField(max_length=255)),
                ('emoji', models.CharField(default=b'', max_length=100)),
                ('picture_url', models.CharField(default=b'', max_length=255)),
                ('slack_name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('mac', models.CharField(max_length=17)),
                ('ip', models.CharField(max_length=15)),
                ('is_present', models.BooleanField(default=False)),
                ('last_scanned', models.DateTimeField()),
                ('last_seen', models.DateTimeField()),
            ],
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('notification_settings', jsonfield.fields.JSONField(default=b'{}')),
                ('is_in_vacation_mode', models.BooleanField(default=False)),
                ('is_in_away_mode', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('home', models.ForeignKey(to='core.Home')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='home',
            field=models.ForeignKey(related_name='devices', to='core.Home'),
        ),
        migrations.AddField(
            model_name='device',
            name='user',
            field=models.ForeignKey(related_name='devices', to=settings.AUTH_USER_MODEL),
        ),
    ]
