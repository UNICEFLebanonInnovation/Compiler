# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-30 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0099_enrollment_justificationnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttype',
            name='description2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]