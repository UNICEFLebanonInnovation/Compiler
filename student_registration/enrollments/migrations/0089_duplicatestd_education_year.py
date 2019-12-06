# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-12-05 10:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0042_setup'),
        ('enrollments', '0088_merge_20191010_0457'),
    ]

    operations = [
        migrations.AddField(
            model_name='duplicatestd',
            name='education_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationYear', verbose_name='\u0627\u0644\u0633\u0646\u0629 \u0627\u0644\u062f\u0631\u0627\u0633\u064a\u0629'),
        ),
    ]
