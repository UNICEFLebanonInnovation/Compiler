# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-04-03 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0019_auto_20200117_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffenroll',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='main record'),
        ),
    ]
