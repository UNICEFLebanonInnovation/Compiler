# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-01-20 10:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0097_documenttype_document_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documenttype',
            name='document_type',
        ),
    ]
