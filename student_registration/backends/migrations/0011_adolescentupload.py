# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0010_useractivity'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdolescentUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('file', models.FileField(upload_to='uploads/adolescent_imports')),
                ('processed', models.BooleanField(default=False)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Uploaded by')),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'Adolescent upload',
                'verbose_name_plural': 'Adolescent uploads',
            },
        ),
    ]
