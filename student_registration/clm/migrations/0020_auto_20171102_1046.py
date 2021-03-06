# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-02 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0019_auto_20171026_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bln',
            name='have_barcode',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u0644\u062f\u064a\u0629 \u0627\u0644\u0628\u0627\u0631\u0643\u0648\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='new_registry',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u064a\u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u0644 \u0644\u0627\u0648\u0644 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='student_outreached',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0645\u0639 \u0627\u0644\u062a\u0644\u0645\u064a\u0630 \u0645\u0646 \u0642\u0628\u0644\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='have_barcode',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u0644\u062f\u064a\u0629 \u0627\u0644\u0628\u0627\u0631\u0643\u0648\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='new_registry',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u064a\u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u0644 \u0644\u0627\u0648\u0644 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='student_outreached',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0645\u0639 \u0627\u0644\u062a\u0644\u0645\u064a\u0630 \u0645\u0646 \u0642\u0628\u0644\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='have_barcode',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u0644\u062f\u064a\u0629 \u0627\u0644\u0628\u0627\u0631\u0643\u0648\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='new_registry',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u064a\u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u0644 \u0644\u0627\u0648\u0644 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='student_outreached',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True, verbose_name='\u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0645\u0639 \u0627\u0644\u062a\u0644\u0645\u064a\u0630 \u0645\u0646 \u0642\u0628\u0644\u061f'),
        ),
    ]
