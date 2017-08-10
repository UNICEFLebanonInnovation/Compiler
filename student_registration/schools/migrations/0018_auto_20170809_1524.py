# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-09 12:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0017_auto_20170708_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='academic_year_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='academic_year_exam_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='academic_year_start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
