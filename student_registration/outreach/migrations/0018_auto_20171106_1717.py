# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-06 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0017_auto_20171106_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='residence_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]