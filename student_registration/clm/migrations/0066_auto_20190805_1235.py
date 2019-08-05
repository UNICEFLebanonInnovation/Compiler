# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-08-05 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0065_auto_20190731_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln',
            name='education_status',
            field=models.CharField(blank=True, choices=[('Never been in formal education', '\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u062e\u0627\u0635\u0629'), ('enrolled in formal educarioh but did not continue', 'Enrolled in formal educarioh but did not continue')], max_length=100, null=True, verbose_name='Education status'),
        ),
        migrations.AddField(
            model_name='bln',
            name='education_status',
            field=models.CharField(blank=True, choices=[('Never been in formal education', '\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u062e\u0627\u0635\u0629'), ('enrolled in formal educarioh but did not continue', 'Enrolled in formal educarioh but did not continue')], max_length=100, null=True, verbose_name='Education status'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='education_status',
            field=models.CharField(blank=True, choices=[('Never been in formal education', '\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u062e\u0627\u0635\u0629'), ('enrolled in formal educarioh but did not continue', 'Enrolled in formal educarioh but did not continue')], max_length=100, null=True, verbose_name='Education status'),
        ),
        migrations.AddField(
            model_name='rs',
            name='education_status',
            field=models.CharField(blank=True, choices=[('Never been in formal education', '\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u062e\u0627\u0635\u0629'), ('enrolled in formal educarioh but did not continue', 'Enrolled in formal educarioh but did not continue')], max_length=100, null=True, verbose_name='Education status'),
        ),
    ]
