# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-07-09 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0056_auto_20190709_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0628\u0637\u0627\u0642\u0629'),
        ),
        migrations.AddField(
            model_name='bln',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0628\u0637\u0627\u0642\u0629'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0628\u0637\u0627\u0642\u0629'),
        ),
        migrations.AddField(
            model_name='rs',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID')], max_length=100, null=True, verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0628\u0637\u0627\u0642\u0629'),
        ),
    ]
