# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-13 13:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0031_auto_20180312_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='education_level',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
