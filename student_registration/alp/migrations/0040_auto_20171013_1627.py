# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-13 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0039_auto_20171009_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='outreach_barcode',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='\u0631\u0642\u0645 \u0627\u0644\u0628\u0627\u0631\u0643\u0648\u062f'),
        ),
    ]