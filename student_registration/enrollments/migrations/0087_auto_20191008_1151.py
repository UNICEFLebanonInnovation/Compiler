# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-10-08 08:51
from __future__ import unicode_literals

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0086_auto_20190928_0838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='duplicatestd',
            name='sysdate',
        ),
        migrations.AddField(
            model_name='duplicatestd',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='duplicatestd',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]
