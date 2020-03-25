# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-17 17:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0106_enrollment_justified_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='justified_by',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u0645\u0628\u0631\u0631'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='justified_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='\u0645\u0628\u0631\u0631'),
        ),
    ]
