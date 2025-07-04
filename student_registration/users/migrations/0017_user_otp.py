# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pyotp


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20240809_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret', models.CharField(default=pyotp.random_base32, max_length=32)),
                ('confirmed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='otp_device', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
