# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-19 07:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0040_auto_20171013_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='exam_result_arabic',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='exam_result_language',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name=' \u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0623\u062c\u0646\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='exam_result_math',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0631\u064a\u0627\u0636\u064a\u0627\u062a'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='exam_result_science',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0639\u0644\u0648\u0645'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='post_exam_result_arabic',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='post_exam_result_language',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name=' \u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0623\u062c\u0646\u0628\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='post_exam_result_math',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0631\u064a\u0627\u0636\u064a\u0627\u062a'),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='post_exam_result_science',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='\u0627\u0644\u0639\u0644\u0648\u0645'),
        ),
    ]
