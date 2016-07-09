# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-04 10:56
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0012_outreach_extra_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='extra_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
