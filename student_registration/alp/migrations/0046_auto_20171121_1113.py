# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-21 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0045_auto_20171114_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outreach',
            name='post_test_room',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='\u063a\u0631\u0641\u0629 \u0627\u0645\u062a\u062d\u0627\u0646 '),
        ),
        migrations.AlterField(
            model_name='outreach',
            name='pre_test_room',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='\u063a\u0631\u0641\u0629 \u0627\u0645\u062a\u062d\u0627\u0646 '),
        ),
    ]
