# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-29 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0028_child_recordnumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='recordnumber',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='\u0631\u0642\u0645 \u0627\u0644\u0633\u062c\u0644'),
        ),
    ]
