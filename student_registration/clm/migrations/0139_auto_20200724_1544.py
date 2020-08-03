# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-07-24 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0138_auto_20200724_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='basic_stationery',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child receive basic stationery?'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='abln',
            name='gender_participate',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did both girls and boys in the same family participate in the class and have access to the phone/device?'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='pss_kit',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child benefit from the PSS kit?'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='remote_learning',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Was the child involved in remote learning?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='basic_stationery',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child receive basic stationery?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='bln',
            name='gender_participate',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did both girls and boys in the same family participate in the class and have access to the phone/device?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='pss_kit',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child benefit from the PSS kit?'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='remote_learning',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Was the child involved in remote learning?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='basic_stationery',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child receive basic stationery?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='gender_participate',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did both girls and boys in the same family participate in the class and have access to the phone/device?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='pss_kit',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child benefit from the PSS kit?'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='remote_learning',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Was the child involved in remote learning?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='basic_stationery',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child receive basic stationery?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the child been reached with awareness messaging on Covid-19 and prevention measures?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_parents_message',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Has the parents been reached with awareness messaging on Covid-19 and prevention measures? '),
        ),
        migrations.AlterField(
            model_name='rs',
            name='gender_participate',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did both girls and boys in the same family participate in the class and have access to the phone/device?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='pss_kit',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Did the child benefit from the PSS kit?'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='remote_learning',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='Was the child involved in remote learning?'),
        ),
    ]