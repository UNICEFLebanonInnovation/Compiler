# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-06 07:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0010_jobs_salarytype'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='with_date_interval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staffenroll',
            name='ending_work',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffenroll',
            name='starting_work',
            field=models.DateField(blank=True, null=True),
        ),
    ]
