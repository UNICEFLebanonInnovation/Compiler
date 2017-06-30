# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-21 13:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0015_auto_20170621_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alpassignmentmatrix',
            name='fail_refer_to',
        ),
        migrations.RemoveField(
            model_name='alpassignmentmatrix',
            name='success_refer_to',
        ),
        migrations.AddField(
            model_name='alpassignmentmatrix',
            name='refer_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='refer_to', to='schools.EducationLevel'),
        ),
    ]
