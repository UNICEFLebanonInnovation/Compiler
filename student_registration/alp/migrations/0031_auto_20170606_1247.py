# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-06 09:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0030_outreach_modified_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
