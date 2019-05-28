# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-09 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0021_auto_20170915_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='total_absences',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_absent_female',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_absent_male',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_attended',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_attended_female',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_attended_male',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_enrolled',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='absence_reason',
            field=models.CharField(blank=True, choices=[('sick', '\u0645\u0631\u0636'), ('no_reason', '\u0644\u0627 \u0633\u0628\u0628'), ('no_transport', '\u0644\u0627 \u0648\u0633\u0627\u0626\u0644 \u0627\u0644\u0646\u0642\u0644'), ('other', '\u0622\u062e\u0631')], max_length=50, null=True),
        ),
    ]
