# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-22 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0071_auto_20180307_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='disabled',
            field=models.BooleanField(default=False, verbose_name='\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u062e\u0627\u0635\u0629'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='dropout_status',
            field=models.BooleanField(default=False, verbose_name=' \u0645\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062a\u0639\u0644\u064a\u0645'),
        ),
    ]
