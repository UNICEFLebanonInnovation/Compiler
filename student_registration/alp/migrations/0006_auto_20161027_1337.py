# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-27 10:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_auto_20161021_1045'),
        ('alp', '0005_auto_20161026_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='outreach',
            name='exam_result_arabic',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20)], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='exam_result_language',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20)], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='exam_result_math',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20)], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='exam_result_science',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20)], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='exam_school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School'),
        ),
        migrations.AddField(
            model_name='outreach',
            name='level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationLevel'),
        ),
        migrations.AddField(
            model_name='outreach',
            name='registered_in_school',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True),
        ),
    ]
