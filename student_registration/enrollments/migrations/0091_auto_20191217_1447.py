# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-12-17 12:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0053_auto_20191008_1151'),
        ('enrollments', '0090_duplicatestd_alp_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='duplicatestd',
            name='outreach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outreach_id', to='alp.Outreach'),
        ),
        migrations.AlterField(
            model_name='duplicatestd',
            name='enrollment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollment_id', to='enrollments.Enrollment'),
        ),
    ]