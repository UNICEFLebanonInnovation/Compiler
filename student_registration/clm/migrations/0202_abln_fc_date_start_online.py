# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-03-09 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0201_auto_20210302_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln_fc',
            name='date_start_online',
            field=models.DateField(blank=True, null=True, verbose_name='Date start online'),
        ),
    ]
