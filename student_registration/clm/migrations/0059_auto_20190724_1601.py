# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-07-24 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0058_auto_20190724_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln',
            name='confirmation_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='abln',
            name='confirmation_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='abln',
            name='confirmation_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='abln',
            name='referral_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='abln',
            name='referral_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='abln',
            name='referral_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='bln',
            name='confirmation_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='bln',
            name='confirmation_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='bln',
            name='confirmation_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='bln',
            name='referral_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='bln',
            name='referral_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='bln',
            name='referral_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='confirmation_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='confirmation_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='confirmation_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='referral_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='referral_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='referral_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='rs',
            name='confirmation_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='rs',
            name='confirmation_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='rs',
            name='confirmation_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Date when the receiving organization confirms accepting the child (or child receiving service)'),
        ),
        migrations.AddField(
            model_name='rs',
            name='referral_date_1',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='rs',
            name='referral_date_2',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
        migrations.AddField(
            model_name='rs',
            name='referral_date_3',
            field=models.DateField(blank=True, null=True, verbose_name='Referral date'),
        ),
    ]
