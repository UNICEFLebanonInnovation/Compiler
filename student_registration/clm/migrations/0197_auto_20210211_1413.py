# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-02-11 12:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0196_auto_20210210_2347'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abln_fc',
            old_name='followup_followup_explain',
            new_name='followup_explain',
        ),
        migrations.AlterField(
            model_name='abln_fc',
            name='fc_type',
            field=models.CharField(blank=True, choices=[('pre1', 'Pre 1'), ('pre2', 'Pre 2'), ('post1', 'Post 1'), ('post2', 'Post 2')], max_length=50, null=True, verbose_name='FC Type'),
        ),
    ]