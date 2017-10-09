# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-09 12:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0023_auto_20170913_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='academic_year_end',
            field=models.DateField(blank=True, null=True, verbose_name=' \u062a\u0627\u0631\u064a\u062e \u0646\u0647\u0627\u064a\u0629 \u0627\u0644\u0639\u0627\u0645 \u0627\u0644\u062f\u0631\u0627\u0633\u064a \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='academic_year_exam_end',
            field=models.DateField(blank=True, null=True, verbose_name='  \u062a\u0627\u0631\u064a\u062e \u0627\u0646\u062a\u0647\u0627\u0621 \u0627\u0644\u0627\u0645\u062a\u062d\u0627\u0646\u0627\u062a \u0627\u062e\u0631 \u0627\u0644\u0633\u0646\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='academic_year_start',
            field=models.DateField(blank=True, null=True, verbose_name='\u062a\u0627\u0631\u064a\u062e \u0628\u062f\u0623 \u0627\u0644\u0639\u0627\u0645 \u0627\u0644\u062f\u0631\u0627\u0633\u064a \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='school',
            name='attendance_range',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0639\u062f\u062f \u0627\u0644\u0627\u064a\u0627\u0645 \u0644\u0627\u062e\u0630 \u0627\u0644\u062d\u0636\u0648\u0631'),
        ),
        migrations.AlterField(
            model_name='school',
            name='director_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=' \u0627\u0633\u0645 \u0645\u062f\u064a\u0631 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='director_phone_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u0645\u062f\u064a\u0631 \u0627\u0644\u0645\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='school',
            name='field_coordinator_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u0627\u0633\u0645 \u0627\u0644\u0645\u0646\u0633\u0642 \u0627\u0644\u0645\u064a\u062f\u0627\u0646\u064a'),
        ),
        migrations.AlterField(
            model_name='school',
            name='is_2nd_shift',
            field=models.BooleanField(default=False, verbose_name=' \u0644\u062f\u0649 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 \u062f\u0648\u0627\u0645 \u0628\u0639\u0636 \u0627\u0644\u0638\u0647\u0631\u061f'),
        ),
        migrations.AlterField(
            model_name='school',
            name='is_alp',
            field=models.BooleanField(default=False, verbose_name=' \u0644\u062f\u0649 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 \u0628\u0631\u0646\u0627\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0643\u062b\u0641\u061f'),
        ),
        migrations.AlterField(
            model_name='school',
            name='it_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=' \u0627\u0633\u0645 \u0645\u0633\u0624\u0648\u0644 \u0627\u0644\u0645\u0643\u0646\u0646\u0629 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='it_phone_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u0645\u0633\u0624\u0648\u0644 \u0627\u0644\u0645\u0643\u0646\u0646\u0629 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='school',
            name='land_phone_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='school',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='locations.Location', verbose_name=' \u0645\u0648\u0642\u0639 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='name',
            field=models.CharField(max_length=255, verbose_name=' \u0627\u0633\u0645 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='number',
            field=models.CharField(max_length=45, unique=True, verbose_name='\u0631\u0642\u0645 \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='school',
            name='number_students_2nd_shift',
            field=models.IntegerField(blank=True, null=True, verbose_name=' \u0639\u062f\u062f \u0627\u0644\u062a\u0644\u0627\u0645\u064a\u0630 \u0627\u0644\u0645\u0633\u062c\u0644\u064a\u0646 \u0641\u064a \u062f\u0648\u0627\u0645 \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'),
        ),
        migrations.AlterField(
            model_name='school',
            name='number_students_alp',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0639\u062f\u062f \u0627\u0644\u062a\u0644\u0627\u0645\u064a\u0630 \u0627\u0644\u0645\u0633\u062c\u0644\u064a\u0646 \u0641\u064a \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0645\u0643\u062b\u0641'),
        ),
    ]
