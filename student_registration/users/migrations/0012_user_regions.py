# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-02 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0006_auto_20191219_1302'),
        ('users', '0011_auto_20191125_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='regions',
            field=models.ManyToManyField(blank=True, related_name='regions', to='locations.Location'),
        ),
    ]