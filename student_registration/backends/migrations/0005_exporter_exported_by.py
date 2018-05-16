# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-15 09:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backends', '0004_notification_school_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporter',
            name='exported_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Exported by'),
        ),
    ]
