# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-05-21 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0079_merge_20190409_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='dropout_date',
            field=models.DateField(blank=True, null=True, verbose_name='dropout date'),
        ),
    ]
