# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-25 07:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0020_auto_20170430_2335'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='exam_result',
            field=models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d/\u0629'), ('failed', '\u0645\u0639\u064a\u062f/\u0629')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_arabic',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u0627\u0644\u0639\u0631\u0628\u064a\u0651\u0629'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_bio',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Biology'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_chemistry',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Chemistry'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_education',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Education'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_geo',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Geography'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_history',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u062a\u0627\u0631\u064a\u062e'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_language',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Language'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_math',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u0631\u064a\u0627\u0636\u064a\u0627\u062a'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_physic',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Physic'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_result_science',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='\u0639\u0644\u0648\u0645'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='exam_total',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Final Grade'),
        ),
    ]
