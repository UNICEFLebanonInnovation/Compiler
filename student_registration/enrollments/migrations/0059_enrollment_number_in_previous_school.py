# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-11 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0058_auto_20171111_0204'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='number_in_previous_school',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Serial number in previous school'),
        ),
    ]
