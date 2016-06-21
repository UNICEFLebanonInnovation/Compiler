# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 13:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0015_auto_20160607_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='father_name',
            field=models.CharField(blank=True, max_length=64L, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='first_name',
            field=models.CharField(blank=True, max_length=64L, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='full_name',
            field=models.CharField(blank=True, max_length=225L, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='last_name',
            field=models.CharField(blank=True, max_length=64L, null=True),
        ),
    ]
