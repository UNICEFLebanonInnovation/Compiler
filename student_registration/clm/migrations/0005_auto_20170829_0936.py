# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-29 06:36
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0004_auto_20170828_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bln',
            name='have_labour',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', 'Yes - Morning'), ('yes_afternoon', 'Yes - Afternoon')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='bln',
            name='labours',
        ),
        migrations.AddField(
            model_name='bln',
            name='labours',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('agriculture', 'Agriculture'), ('building', 'Building'), ('manufacturing', 'Manufacturing'), ('retail_store', 'Retail / Store'), ('begging', 'Begging'), ('other_many_other', 'Other (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'), ('other', '\u0622\u062e\u0631')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='bln',
            name='referral',
        ),
        migrations.AddField(
            model_name='bln',
            name='referral',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('from_same_ngo', 'Referral from the same NGO'), ('from_other_ngo', 'Referral from an other NGO'), ('form_official_reference', 'Referral from an official reference (Mukhtar, Municipality, School Director, etc.)'), ('from_host_community', 'Referral from the host community'), ('from_displaced_community', 'Referral from the displaced community')], max_length=100, null=True), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='have_labour',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', 'Yes - Morning'), ('yes_afternoon', 'Yes - Afternoon')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='cbece',
            name='labours',
        ),
        migrations.AddField(
            model_name='cbece',
            name='labours',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('agriculture', 'Agriculture'), ('building', 'Building'), ('manufacturing', 'Manufacturing'), ('retail_store', 'Retail / Store'), ('begging', 'Begging'), ('other_many_other', 'Other (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'), ('other', '\u0622\u062e\u0631')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='cbece',
            name='referral',
        ),
        migrations.AddField(
            model_name='cbece',
            name='referral',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('from_same_ngo', 'Referral from the same NGO'), ('from_other_ngo', 'Referral from an other NGO'), ('form_official_reference', 'Referral from an official reference (Mukhtar, Municipality, School Director, etc.)'), ('from_host_community', 'Referral from the host community'), ('from_displaced_community', 'Referral from the displaced community')], max_length=100, null=True), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='rs',
            name='have_labour',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', 'Yes - Morning'), ('yes_afternoon', 'Yes - Afternoon')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
        migrations.RemoveField(
            model_name='rs',
            name='labours',
        ),
        migrations.AddField(
            model_name='rs',
            name='labours',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('agriculture', 'Agriculture'), ('building', 'Building'), ('manufacturing', 'Manufacturing'), ('retail_store', 'Retail / Store'), ('begging', 'Begging'), ('other_many_other', 'Other (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)'), ('other', '\u0622\u062e\u0631')], max_length=50, null=True), blank=True, null=True, size=None),
        ),
    ]