# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-10 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0027_auto_20171106_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='certified_foreign_language',
            field=models.CharField(blank=True, choices=[('French', '\u0627\u0644\u0641\u0631\u0646\u0633\u064a\u0629'), ('English', '\u0627\u0644\u0627\u0646\u0643\u0644\u064a\u0632\u064a\u0629'), ('French & English', 'French & English')], max_length=100, null=True, verbose_name='Certified foreign language'),
        ),
        migrations.AddField(
            model_name='school',
            name='comments',
            field=models.TextField(blank=True, null=True, verbose_name='Comments'),
        ),
        migrations.AddField(
            model_name='school',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='School email'),
        ),
        migrations.AddField(
            model_name='school',
            name='fax_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='School fax number'),
        ),
        migrations.AddField(
            model_name='school',
            name='weekend',
            field=models.CharField(blank=True, choices=[('Friday', '\u0627\u0644\u062c\u0645\u0639\u0629'), ('Saturday', '\u0627\u0644\u0633\u0628\u062a')], max_length=100, null=True, verbose_name='School weekends'),
        ),
    ]
