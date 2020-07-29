# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-07-29 07:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0143_auto_20200729_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
    ]
