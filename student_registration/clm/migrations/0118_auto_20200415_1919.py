# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-04-15 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0117_auto_20200414_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='second_phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u0647\u0644 \u064a\u0648\u062c\u062f \u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u062b\u0627\u0646\u064a\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='second_phone_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u062a\u0623\u0643\u064a\u062f \u0631\u0642\u0645 \u0627\u0644\u062a\u0644\u0641\u0648\u0646 \u0627\u0644\u062b\u0627\u0646\u064a'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='second_phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u0647\u0644 \u064a\u0648\u062c\u062f \u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u062b\u0627\u0646\u064a\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='second_phone_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u062a\u0623\u0643\u064a\u062f \u0631\u0642\u0645 \u0627\u0644\u062a\u0644\u0641\u0648\u0646 \u0627\u0644\u062b\u0627\u0646\u064a'),
        ),
        migrations.AlterField(
            model_name='inclusion',
            name='second_phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u0647\u0644 \u064a\u0648\u062c\u062f \u0631\u0642\u0645 \u0647\u0627\u062a\u0641 \u062b\u0627\u0646\u064a\u061f'),
        ),
        migrations.AlterField(
            model_name='inclusion',
            name='second_phone_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u062a\u0623\u0643\u064a\u062f \u0631\u0642\u0645 \u0627\u0644\u062a\u0644\u0641\u0648\u0646 \u0627\u0644\u062b\u0627\u0646\u064a'),
        ),
    ]
