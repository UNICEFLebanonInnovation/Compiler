# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-03 07:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0033_auto_20170801_1415'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enrollment',
            old_name='old_or_new',
            new_name='new_registry',
        ),
    ]