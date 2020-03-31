# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-25 06:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0059_auto_20200325_0757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='implemented_de_2',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], default='no', max_length=3, verbose_name='\u0647\u0644 \u0646\u0641\u0630\u062a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='implemented_de_3',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], default='no', max_length=3, verbose_name='\u0647\u0644 \u0646\u0641\u0630\u062a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='implemented_de_9',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], default='no', max_length=3, verbose_name='\u0647\u0644 \u0646\u0641\u0630\u062a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='implemented_de_prep',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], default='no', max_length=3, verbose_name='\u0647\u0644 \u0646\u0641\u0630\u062a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
    ]