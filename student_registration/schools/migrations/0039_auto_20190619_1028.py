# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-06-19 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0038_auto_20190619_0156'),
    ]

    operations = [
        migrations.AddField(
            model_name='clmround',
            name='end_date_abln_edit',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clmround',
            name='end_date_bln_edit',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clmround',
            name='end_date_cbece_edit',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clmround',
            name='start_date_abln_edit',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clmround',
            name='start_date_bln_edit',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clmround',
            name='start_date_cbece_edit',
            field=models.DateField(blank=True, null=True),
        ),
    ]