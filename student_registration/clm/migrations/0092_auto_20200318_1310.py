# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-18 11:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0091_auto_20200318_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='follow_up_type',
            field=models.CharField(blank=True, choices=[('none', '----------'), ('Phone', '\u0625\u062a\u0635\u0627\u0644 \u0647\u0627\u062a\u0641\u064a'), ('House visit', '\u0632\u064a\u0627\u0631\u0629 \u0645\u0646\u0632\u0644\u064a\u0629'), ('Family Visit', '\u0632\u064a\u0627\u0631\u0629 \u0627\u0644\u0623\u0647\u0644 \u0644\u0644\u0645\u0631\u0643\u0632')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0645\u062a\u0627\u0628\u0639\u0629'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='follow_up_type',
            field=models.CharField(blank=True, choices=[('none', '----------'), ('Phone', '\u0625\u062a\u0635\u0627\u0644 \u0647\u0627\u062a\u0641\u064a'), ('House visit', '\u0632\u064a\u0627\u0631\u0629 \u0645\u0646\u0632\u0644\u064a\u0629'), ('Family Visit', '\u0632\u064a\u0627\u0631\u0629 \u0627\u0644\u0623\u0647\u0644 \u0644\u0644\u0645\u0631\u0643\u0632')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0645\u062a\u0627\u0628\u0639\u0629'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='follow_up_type',
            field=models.CharField(blank=True, choices=[('none', '----------'), ('Phone', '\u0625\u062a\u0635\u0627\u0644 \u0647\u0627\u062a\u0641\u064a'), ('House visit', '\u0632\u064a\u0627\u0631\u0629 \u0645\u0646\u0632\u0644\u064a\u0629'), ('Family Visit', '\u0632\u064a\u0627\u0631\u0629 \u0627\u0644\u0623\u0647\u0644 \u0644\u0644\u0645\u0631\u0643\u0632')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0645\u062a\u0627\u0628\u0639\u0629'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='follow_up_type',
            field=models.CharField(blank=True, choices=[('none', '----------'), ('Phone', '\u0625\u062a\u0635\u0627\u0644 \u0647\u0627\u062a\u0641\u064a'), ('House visit', '\u0632\u064a\u0627\u0631\u0629 \u0645\u0646\u0632\u0644\u064a\u0629'), ('Family Visit', '\u0632\u064a\u0627\u0631\u0629 \u0627\u0644\u0623\u0647\u0644 \u0644\u0644\u0645\u0631\u0643\u0632')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0645\u062a\u0627\u0628\u0639\u0629'),
        ),
    ]