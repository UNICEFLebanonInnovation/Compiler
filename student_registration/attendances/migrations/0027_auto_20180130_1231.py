# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-30 10:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0050_auto_20171218_1026'),
        ('schools', '0034_auto_20171218_1026'),
        ('attendances', '0026_auto_20171114_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='alp_round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='alp.ALPRound'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='education_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationYear'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='school_type',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
    ]
