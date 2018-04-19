# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-13 09:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0050_auto_20171218_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='alpround',
            name='round_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Round end date'),
        ),
        migrations.AddField(
            model_name='alpround',
            name='round_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Round start date'),
        ),
    ]