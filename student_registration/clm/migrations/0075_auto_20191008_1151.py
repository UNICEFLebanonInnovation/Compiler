# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-10-08 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0074_merge_20191008_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='cycle_completed',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0643\u0645\u0627\u0644 \u0627\u0644\u062f\u0648\u0631\u0629 \u0628\u0646\u062c\u0627\u062d'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='enrolled_at_school',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='cycle_completed',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0643\u0645\u0627\u0644 \u0627\u0644\u062f\u0648\u0631\u0629 \u0628\u0646\u062c\u0627\u062d'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='enrolled_at_school',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='cycle_completed',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0643\u0645\u0627\u0644 \u0627\u0644\u062f\u0648\u0631\u0629 \u0628\u0646\u062c\u0627\u062d'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='enrolled_at_school',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='cycle_completed',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0643\u0645\u0627\u0644 \u0627\u0644\u062f\u0648\u0631\u0629 \u0628\u0646\u062c\u0627\u062d'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='enrolled_at_school',
            field=models.BooleanField(default=False, verbose_name='\u0627\u0646\u0642\u0631 \u062e\u0627\u0646\u0629 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0625\u0630\u0627 \u062a\u0645 \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0641\u064a \u0627\u0644\u0645\u062f\u0631\u0633\u0629'),
        ),
    ]
