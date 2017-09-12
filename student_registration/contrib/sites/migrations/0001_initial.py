# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.sites.models
<<<<<<< HEAD
=======
from django.contrib.sites.models import _simple_domain_name_validator
from django.db import migrations, models
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1


class Migration(migrations.Migration):

<<<<<<< HEAD
    dependencies = [
    ]
=======
    dependencies = []
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
<<<<<<< HEAD
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('domain', models.CharField(verbose_name='domain name', max_length=100, validators=[django.contrib.sites.models._simple_domain_name_validator])),
                ('name', models.CharField(verbose_name='display name', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'sites',
                'verbose_name': 'site',
                'db_table': 'django_site',
                'ordering': ('domain',),
            },
            managers=[
                (b'objects', django.contrib.sites.models.SiteManager()),
=======
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(
                    max_length=100, verbose_name='domain name', validators=[_simple_domain_name_validator]
                )),
                ('name', models.CharField(max_length=50, verbose_name='display name')),
            ],
            options={
                'ordering': ('domain',),
                'db_table': 'django_site',
                'verbose_name': 'site',
                'verbose_name_plural': 'sites',
            },
            bases=(models.Model,),
            managers=[
                ('objects', django.contrib.sites.models.SiteManager()),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            ],
        ),
    ]
