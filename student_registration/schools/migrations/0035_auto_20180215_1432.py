# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-15 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0034_auto_20171218_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpassignmentmatrix',
            name='range_end',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alpassignmentmatrix',
            name='range_start',
            field=models.FloatField(blank=True, null=True),
        ),
    ]