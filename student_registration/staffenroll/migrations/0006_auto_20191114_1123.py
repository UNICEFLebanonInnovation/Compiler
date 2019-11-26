# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-11-14 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0009_auto_20191008_1151'),
        ('staffenroll', '0005_auto_20191008_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffenroll',
            name='student',
        ),
        migrations.AddField(
            model_name='staffenroll',
            name='staff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_enrollment', to='staffs.Staffs'),
        ),
    ]
