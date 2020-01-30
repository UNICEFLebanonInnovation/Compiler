# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-30 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0081_auto_20200121_0022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='referral_partner_1',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='referral_partner_2',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='referral_partner_3',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='referral_partner_1',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='referral_partner_2',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='referral_partner_3',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='referral_partner_1',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='referral_partner_2',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='referral_partner_3',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='referral_partner_1',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='referral_partner_2',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='referral_partner_3',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='School / Center'),
        ),
    ]
