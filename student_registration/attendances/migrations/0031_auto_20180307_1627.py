# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-07 14:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0030_absentee_last_modification_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='schools.School'),
        ),
    ]
