# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0065_alter_msccattendance_education_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msccattendance',
            name='education_program',
            field=models.CharField(blank=True, choices=[('BLN Level 1', 'BLN Level 1'), ('BLN Level 2', 'BLN Level 2'), ('BLN Level 3', 'BLN Level 3'), ('BLN Catch-up', 'BLN Catch-up'), ('ABLN Level 1', 'ABLN Level 1'), ('ABLN Level 2', 'ABLN Level 2'), ('ABLN Catch-up', 'ABLN Catch-up'), ('YBLN Level 1', 'YBLN Level 1'), ('YBLN Level 2', 'YBLN Level 2'), ('YBLN Catch-up', 'YBLN Catch-up'), ('YFS Level 1', 'YFS Level 1'), ('YFS Level 2', 'YFS Level 2'), ('YFS Level 1 - RS Grade 9', 'YFS Level 1 - RS Grade 9'), ('YFS Level 2 - RS Grade 9', 'YFS Level 2 - RS Grade 9'), ('CBECE Level 1', 'CBECE Level 1'), ('CBECE Level 2', 'CBECE Level 2'), ('CBECE Level 3', 'CBECE Level 3'), ('CBECE Catch-up', 'CBECE Catch-up'), ('RS Grade 1', 'RS Grade 1'), ('RS Grade 2', 'RS Grade 2'), ('RS Grade 3', 'RS Grade 3'), ('RS Grade 4', 'RS Grade 4'), ('RS Grade 5', 'RS Grade 5'), ('RS Grade 6', 'RS Grade 6'), ('RS Grade 7', 'RS Grade 7'), ('RS Grade 8', 'RS Grade 8'), ('RS Grade 9', 'RS Grade 9'), ('Summer RS Grade 1', 'Summer RS Grade 1'), ('Summer RS Grade 2', 'Summer RS Grade 2'), ('Summer RS Grade 3', 'Summer RS Grade 3'), ('Summer RS Grade 4', 'Summer RS Grade 4'), ('Summer RS Grade 5', 'Summer RS Grade 5'), ('Summer RS Grade 6', 'Summer RS Grade 6'), ('Summer RS Grade 7', 'Summer RS Grade 7'), ('Summer RS Grade 8', 'Summer RS Grade 8'), ('Summer RS Grade 9', 'Summer RS Grade 9'), ('ECD', 'ECD')], max_length=200, null=True, verbose_name='Education Program'),
        ),
    ]
