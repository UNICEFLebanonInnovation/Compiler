# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-28 05:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0051_auto_20180413_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpround',
            name='round_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='\u062a\u0627\u0631\u064a\u062e \u0646\u0647\u0627\u064a\u0629 \u0627\u0644\u062c\u0648\u0644\u0629'),
        ),
        migrations.AlterField(
            model_name='alpround',
            name='round_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='\u062a\u0627\u0631\u064a\u062e \u0628\u062f\u0621 \u0627\u0644\u062c\u0648\u0644\u0629'),
        ),
    ]
