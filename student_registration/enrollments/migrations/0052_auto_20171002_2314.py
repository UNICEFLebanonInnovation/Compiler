# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-02 20:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0051_auto_20171002_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='enrollments.Enrollment'),
        ),
    ]
