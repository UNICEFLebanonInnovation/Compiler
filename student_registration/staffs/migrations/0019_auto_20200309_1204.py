# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-09 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0018_auto_20200117_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffs',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='\u0625\u0633\u0645 \u0627\u0644\u0637\u0641\u0644'),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='last_name',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='\u0634\u0647\u0631\u0629 \u0627\u0644\u0637\u0641\u0644'),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='mother_fullname',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='\u0627\u0633\u0645 \u0627\u0644\u0623\u0645'),
        ),
    ]
