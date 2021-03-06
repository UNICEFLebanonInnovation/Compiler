# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-03-28 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0019_auto_20200317_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffs',
            name='pic_2ndshiftcertificate',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Picture of the second shift certificate'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='pic_commitment',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Picture of the commitment'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='pic_iban',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Picture of the iban'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='pic_identification',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Picture of Identy'),
        ),
    ]
