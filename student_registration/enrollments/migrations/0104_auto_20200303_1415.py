# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-03 12:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0103_enrollment_is_justified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='is_justified',
            field=models.BooleanField(default=False),
        ),
    ]