# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-10 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0066_auto_20180130_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='disabled',
            field=models.BooleanField(default=False, verbose_name='disabled'),
        ),
    ]
