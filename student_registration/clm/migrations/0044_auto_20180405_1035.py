# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-05 07:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0043_auto_20180326_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rs',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', ' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'), ('repeat_level', '\u0646\u0639\u0645'), ('graduated_next_level', '\u0643\u0644\u0627')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
    ]
