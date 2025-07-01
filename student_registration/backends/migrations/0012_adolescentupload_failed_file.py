# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0011_adolescentupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='adolescentupload',
            name='failed_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/adolescent_imports'),
        ),
    ]
