# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-04-22 13:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0121_auto_20200422_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='main_caregiver_nationality',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='students.Nationality', verbose_name='\u062c\u0646\u0633\u064a\u0629 \u0648\u0644\u064a \u0627\u0644\u0623\u0645\u0631'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='main_caregiver_nationality',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='students.Nationality', verbose_name='\u062c\u0646\u0633\u064a\u0629 \u0648\u0644\u064a \u0627\u0644\u0623\u0645\u0631'),
        ),
        migrations.AlterField(
            model_name='inclusion',
            name='main_caregiver_nationality',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='students.Nationality', verbose_name='\u062c\u0646\u0633\u064a\u0629 \u0648\u0644\u064a \u0627\u0644\u0623\u0645\u0631'),
        ),
    ]