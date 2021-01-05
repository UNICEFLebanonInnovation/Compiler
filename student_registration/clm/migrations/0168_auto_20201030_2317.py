# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-10-30 21:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0167_auto_20201030_2312'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abln',
            old_name='covid_session_modality1',
            new_name='covid_session_modality',
        ),
        migrations.RenameField(
            model_name='abln',
            old_name='followup_session_modality1',
            new_name='followup_session_modality',
        ),
        migrations.RenameField(
            model_name='abln',
            old_name='pss_session_modality1',
            new_name='pss_session_modality',
        ),
        migrations.RenameField(
            model_name='bln',
            old_name='covid_session_modality1',
            new_name='covid_session_modality',
        ),
        migrations.RenameField(
            model_name='bln',
            old_name='followup_session_modality1',
            new_name='followup_session_modality',
        ),
        migrations.RenameField(
            model_name='bln',
            old_name='pss_session_modality1',
            new_name='pss_session_modality',
        ),
        migrations.RenameField(
            model_name='cbece',
            old_name='covid_session_modality1',
            new_name='covid_session_modality',
        ),
        migrations.RenameField(
            model_name='cbece',
            old_name='followup_session_modality1',
            new_name='followup_session_modality',
        ),
        migrations.RenameField(
            model_name='cbece',
            old_name='pss_session_modality1',
            new_name='pss_session_modality',
        ),
        migrations.RenameField(
            model_name='rs',
            old_name='covid_session_modality1',
            new_name='covid_session_modality',
        ),
        migrations.RenameField(
            model_name='rs',
            old_name='followup_session_modality1',
            new_name='followup_session_modality',
        ),
        migrations.RenameField(
            model_name='rs',
            old_name='pss_session_modality1',
            new_name='pss_session_modality',
        ),
    ]