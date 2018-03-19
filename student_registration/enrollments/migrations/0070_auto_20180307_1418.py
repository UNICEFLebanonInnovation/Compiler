# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-07 12:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0069_disabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_arabic',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_artistic',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u0641\u0646\u064a'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_bio',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0639\u0644\u0648\u0645 \u0627\u0644\u062d\u064a\u0627\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_chemistry',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0643\u064a\u0645\u064a\u0627\u0621'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_education',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u062a\u0631\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_geo',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u062c\u063a\u0631\u0627\u0641\u064a\u0627'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_history',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u062a\u0627\u0631\u064a\u062e'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_language',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0644\u063a\u0629 \u0627\u062c\u0646\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_linguistic_ar',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u0644\u063a\u0648\u064a/\u0639\u0631\u0628\u064a'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_linguistic_en',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u063a\u0648\u064a/\u0644\u063a\u0629 \u0627\u062c\u0646\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_math',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0627\u0644\u0631\u064a\u0627\u0636\u064a\u0627\u062a'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_mathematics',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u0639\u0644\u0645\u064a/\u0631\u064a\u0627\u0636\u064a\u0627\u062a'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_physic',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0641\u064a\u0632\u064a\u0627\u0621'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_physical',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0645\u062c\u0627\u0644 \u0627\u0644\u0631\u064a\u0627\u0636\u0629 \u0627\u0644\u0628\u062f\u0646\u064a\u0629 \u0648\u0627\u0644\u062c\u0633\u062f\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_science',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='\u0627\u0644\u0639\u0644\u0648\u0645'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_sciences',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u0639\u0644\u0645\u064a/\u0639\u0644\u0648\u0645'),
        ),
        migrations.AlterField(
            model_name='enrollmentgrading',
            name='exam_result_sociology',
            field=models.CharField(blank=True, default=None, max_length=6, null=True, verbose_name='\u0627\u0644\u0645\u062c\u0627\u0644 \u0627\u0644\u0627\u062c\u062a\u0645\u0627\u0639\u064a'),
        ),
    ]
