# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-18 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_user_regions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='staff_password',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='staff password'),
        ),
    ]
