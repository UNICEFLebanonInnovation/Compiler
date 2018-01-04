# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-18 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0033_auto_20171128_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerorganization',
            name='schools',
            field=models.ManyToManyField(blank=True, to='schools.School'),
        ),
        migrations.AlterField(
            model_name='school',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u0627\u0644\u0628\u0631\u064a\u062f \u0627\u0644\u0627\u0644\u0643\u062a\u0631\u0648\u0646\u064a \u0627\u0644\u062e\u0627\u0635 \u0628\u0627\u0644\u0645\u062f\u0631\u0633\u0629 '),
        ),
        migrations.AlterField(
            model_name='school',
            name='is_alp',
            field=models.BooleanField(default=False, verbose_name=' \u0644\u062f\u0649 \u0627\u0644\u0645\u062f\u0631\u0633\u0629 \u0628\u0631\u0646\u0627\u0645\u062c ALP\u061f'),
        ),
        migrations.AlterField(
            model_name='school',
            name='number_students_2nd_shift',
            field=models.IntegerField(blank=True, null=True, verbose_name=' \u0639\u062f\u062f \u0627\u0644\u062a\u0644\u0627\u0645\u0630\u0629 \u0627\u0644\u0645\u062a\u0648\u0642\u0639 \u062a\u0633\u062c\u064a\u0644\u0647\u0645 \u0641\u064a \u062f\u0648\u0627\u0645 \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'),
        ),
        migrations.AlterField(
            model_name='school',
            name='number_students_alp',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0639\u062f\u062f \u0627\u0644\u062a\u0644\u0627\u0645\u0630\u0629 \u0627\u0644\u0645\u062a\u0648\u0642\u0639 \u062a\u0633\u062c\u064a\u0644\u0647\u0645 \u0641\u064a ALP'),
        ),
    ]