# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-06 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0013_auto_20200106_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffattend',
            name='isattend',
            field=models.NullBooleanField(default=False),
        ),
    ]