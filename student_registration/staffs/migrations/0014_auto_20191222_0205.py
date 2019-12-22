# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-12-22 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0013_remove_staffs_staff_seq'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='staff_seq',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]