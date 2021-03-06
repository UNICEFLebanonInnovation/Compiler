# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-13 08:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0033_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='outreach',
            name='have_barcode',
            field=models.CharField(blank=True, choices=[(1, '\u0646\u0639\u0645'), (0, '\u0643\u0644\u0627')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='new_registry',
            field=models.CharField(blank=True, choices=[(1, '\u0646\u0639\u0645'), (0, '\u0643\u0644\u0627')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='outreach_barcode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='outreach',
            name='student_outreached',
            field=models.CharField(blank=True, choices=[(1, '\u0646\u0639\u0645'), (0, '\u0643\u0644\u0627')], max_length=50, null=True),
        ),
    ]
