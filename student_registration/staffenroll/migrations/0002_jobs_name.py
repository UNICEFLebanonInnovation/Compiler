# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-02 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='name',
            field=models.CharField(default=0, max_length=45, unique=True, verbose_name='Jobs'),
        ),
    ]
