# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-02-09 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0056_auto_20170209_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaintcategory',
            name='complaint_type',
            field=models.CharField(blank=True, choices=[('distribution', 'CARD DISTRIBUTION'), ('card', 'CARD'), ('payment', 'PAYMENT'), ('school', 'SCHOOL-RELATED'), ('other', 'Other')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='complaintcategory',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
