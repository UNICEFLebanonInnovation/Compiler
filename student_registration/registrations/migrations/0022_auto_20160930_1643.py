# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-30 13:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_auto_20160930_1435'),
        ('registrations', '0021_auto_20160920_2201'),
    ]

    operations = [
        migrations.CreateModel(
            name='WFPDistributionSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('location', models.ManyToManyField(to='locations.Location')),
            ],
        ),
        migrations.AddField(
            model_name='registeringadult',
            name='wfp_distribution_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.WFPDistributionSite'),
        ),
    ]
