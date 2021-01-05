# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-09-11 19:39
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0032_auto_20200414_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='informal_education_type',
            field=models.CharField(blank=True, choices=[('ALP', 'ALP'), ('BLN', '\u0625\u062d\u0627\u0644\u0629 \u0645\u0646 \u0628\u0631\u0646\u0627\u0645\u062c BLN \u0625\u0627\u0644\u0649  ABLN programme'), ('CBECE', 'CB-ECE'), ('SALP', 'SALP')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='child',
            name='last_informal_education',
            field=models.CharField(blank=True, choices=[('ALP', 'ALP'), ('BLN', '\u0625\u062d\u0627\u0644\u0629 \u0645\u0646 \u0628\u0631\u0646\u0627\u0645\u062c BLN \u0625\u0627\u0644\u0649  ABLN programme'), ('CB-ECE', 'CB-ECE'), ('SALP', 'SALP'), ('Prep.ALP', 'Prep.ALP'), ('Special_EDU_Dis', 'Special_EDU_Dis')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='child',
            name='referral_reason',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('ALP', 'ALP'), ('BLN', '\u0625\u062d\u0627\u0644\u0629 \u0645\u0646 \u0628\u0631\u0646\u0627\u0645\u062c BLN \u0625\u0627\u0644\u0649  ABLN programme'), ('CBECE', 'CB-ECE'), ('SALP', 'SALP')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
    ]