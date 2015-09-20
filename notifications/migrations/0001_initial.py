# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child_name', models.CharField(max_length=200, null=True, blank=True)),
                ('react_to', jsonfield.fields.JSONField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Slack',
            fields=[
                ('notifier_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.Notifier')),
                ('api_key', models.CharField(max_length=255)),
                ('channel', models.CharField(max_length=255)),
                ('username', models.CharField(default=b'Phoebe', max_length=255)),
                ('icon', models.URLField(default=b'https://i2.wp.com/s3.amazonaws.com/rapgenius/d43e2b45855a8bde06330c076628b2a7.jpeg', max_length=500)),
            ],
            options={
                'abstract': False,
            },
            bases=('notifications.notifier',),
        ),
        migrations.AddField(
            model_name='notifier',
            name='home',
            field=models.ForeignKey(blank=True, to='core.Home', null=True),
        ),
    ]
