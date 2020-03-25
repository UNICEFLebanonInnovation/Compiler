# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-22 17:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0055_auto_20200322_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='c9_evaluation',
            field=models.TextField(blank=True, null=True, verbose_name='Evaluation on the interventions '),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='c9_interventions',
            field=models.TextField(blank=True, null=True, verbose_name='Interventions taken in the cycle'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='c9_challanges_difficulties_de',
            field=models.TextField(blank=True, null=True, verbose_name='Challenges that faces the implementation'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='c9_used_method_de',
            field=models.TextField(blank=True, null=True, verbose_name='Methods that are used in distance education'),
        ),
    ]
