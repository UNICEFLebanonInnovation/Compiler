# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-18 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0070_auto_20190823_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='education_status',
            field=models.CharField(blank=True, choices=[('out of school', 'Out of school'), ('enrolled in formal education but did not continue', 'Enrolled in formal education but did not continue'), ('enrolled in ABLN', 'Enrolled in ABLN')], max_length=100, null=True, verbose_name='\u0627\u0644\u0648\u0636\u0639 \u0627\u0644\u062f\u0631\u0627\u0633\u064a'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='education_status',
            field=models.CharField(blank=True, choices=[('out of school', 'Out of school'), ('enrolled in formal education but did not continue', 'Enrolled in formal education but did not continue'), ('enrolled in ABLN', 'Enrolled in ABLN')], max_length=100, null=True, verbose_name='\u0627\u0644\u0648\u0636\u0639 \u0627\u0644\u062f\u0631\u0627\u0633\u064a'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='education_status',
            field=models.CharField(blank=True, choices=[('out of school', 'Out of school'), ('enrolled in formal education but did not continue', 'Enrolled in formal education but did not continue'), ('enrolled in ABLN', 'Enrolled in ABLN')], max_length=100, null=True, verbose_name='\u0627\u0644\u0648\u0636\u0639 \u0627\u0644\u062f\u0631\u0627\u0633\u064a'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='education_status',
            field=models.CharField(blank=True, choices=[('out of school', 'Out of school'), ('enrolled in formal education but did not continue', 'Enrolled in formal education but did not continue'), ('enrolled in ABLN', 'Enrolled in ABLN')], max_length=100, null=True, verbose_name='\u0627\u0644\u0648\u0636\u0639 \u0627\u0644\u062f\u0631\u0627\u0633\u064a'),
        ),
    ]