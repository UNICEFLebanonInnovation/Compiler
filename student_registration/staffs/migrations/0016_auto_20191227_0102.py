# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-12-26 23:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0015_staffs_first_education_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='cert_origin',
            field=models.CharField(blank=True, max_length=70, null=True, verbose_name='Speciality'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='speciality',
            field=models.CharField(blank=True, max_length=70, null=True, verbose_name='Speciality'),
        ),
    ]