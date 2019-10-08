# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-10-08 08:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0004_auto_20190928_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobs',
            name='hourrate',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0627\u0644\u0642\u064a\u0645\u0629'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='current_hourrate',
            field=models.IntegerField(blank=True, null=True, verbose_name='\u0627\u0644\u0642\u064a\u0645\u0629'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffenroll.Jobs', verbose_name='Jobs'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='staffenroll.Subjects', verbose_name='\u0627\u0644\u0645\u0648\u0627\u062f'),
        ),
    ]