# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-01 15:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0025_auto_20171201_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='barcode_subset',
            field=models.CharField(blank=True, db_index=True, max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='barcode_number',
            field=models.CharField(blank=True, db_index=True, max_length=45, null=True),
        ),
    ]
