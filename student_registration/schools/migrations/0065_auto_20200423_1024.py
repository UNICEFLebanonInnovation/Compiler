# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-04-23 07:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0064_auto_20200413_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='classroom_type',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='classroom_type',
            field=models.CharField(blank=True, choices=[('PV', 'Private School'), ('PU', 'Public School')], max_length=2, null=True),
        ),
    ]