# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-10-30 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0168_auto_20201030_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abln',
            name='covid_session_modality',
        ),
        migrations.RemoveField(
            model_name='abln',
            name='followup_session_modality',
        ),
        migrations.RemoveField(
            model_name='abln',
            name='pss_session_modality',
        ),
        migrations.RemoveField(
            model_name='bln',
            name='covid_session_modality',
        ),
        migrations.RemoveField(
            model_name='bln',
            name='followup_session_modality',
        ),
        migrations.RemoveField(
            model_name='bln',
            name='pss_session_modality',
        ),
        migrations.RemoveField(
            model_name='cbece',
            name='covid_session_modality',
        ),
        migrations.RemoveField(
            model_name='cbece',
            name='followup_session_modality',
        ),
        migrations.RemoveField(
            model_name='cbece',
            name='pss_session_modality',
        ),
        migrations.RemoveField(
            model_name='rs',
            name='covid_session_modality',
        ),
        migrations.RemoveField(
            model_name='rs',
            name='followup_session_modality',
        ),
        migrations.RemoveField(
            model_name='rs',
            name='pss_session_modality',
        ),
    ]