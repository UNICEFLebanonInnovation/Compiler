# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-10-06 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0086_auto_20190928_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='nb_consecutiveabsences',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
