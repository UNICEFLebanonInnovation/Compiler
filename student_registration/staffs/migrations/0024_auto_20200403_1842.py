# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-04-03 15:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0023_auto_20200402_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='staffs',
            name='worklist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffs.Worklist', verbose_name='List of work'),
        ),
    ]
