# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-29 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0020_auto_20200328_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='pic_certificate',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Picture of the certificate'),
        ),
    ]
