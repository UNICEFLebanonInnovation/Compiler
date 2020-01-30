# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-17 08:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffenroll', '0018_staffenroll_school_am'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffattend',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='staffenroll.Jobs', verbose_name='\u0646\u0648\u0639 \u0627\u0644\u0639\u0645\u0644'),
        ),
        migrations.AlterField(
            model_name='staffattend',
            name='staff',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='staffs.Staffs', verbose_name='\u0627\u0644\u0639\u0627\u0645\u0644'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffenroll.Jobs', verbose_name='\u0648\u0638\u0627\u0626\u0641'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='shift',
            field=models.CharField(blank=True, choices=[('D', '\u0646\u0647\u0627\u0631'), ('N', '\u0644\u064a\u0644')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='weeklyhours_noclass',
            field=models.IntegerField(default=0, verbose_name='\u0639\u062f\u062f \u0627\u0644\u0633\u0627\u0639\u0627\u062a \u0641\u064a \u0627\u0644\u0623\u0633\u0628\u0648\u0639'),
        ),
        migrations.AlterField(
            model_name='staffenroll',
            name='work',
            field=models.CharField(blank=True, max_length=150, verbose_name='\u0627\u0644\u0639\u0645\u0644 \u0627\u0644\u0631\u0626\u064a\u0633\u064a'),
        ),
    ]