# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-15 16:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0014_auto_20161109_1414'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alpround',
            options={'ordering': ['id'], 'verbose_name': 'ALP Round'},
        ),
        migrations.AlterModelOptions(
            name='outreach',
            options={'ordering': ['id'], 'verbose_name': 'Post Test'},
        ),
    ]
