# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-01-19 12:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0127_auto_20210118_1704'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluationdt',
            name='classroom',
        ),
        migrations.RemoveField(
            model_name='evaluationdt',
            name='evaluation',
        ),
        migrations.RemoveField(
            model_name='evaluationdt',
            name='subject',
        ),
        migrations.DeleteModel(
            name='Subject',
        ),
        migrations.DeleteModel(
            name='EvaluationDt',
        ),
    ]
