# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-02-16 06:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0020_auto_20161230_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='idtype',
            name='inuse',
            field=models.BooleanField(default=True),
        ),
    ]
