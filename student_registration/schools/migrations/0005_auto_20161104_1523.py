# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-04 13:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0004_auto_20161104_0914'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partnerorganization',
            options={'ordering': ['name']},
        ),
    ]
