# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-04-12 07:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

        ('staffenroll', '0019_auto_20200117_1032'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticAttend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('attenddate', models.DateField()),
                ('hoursofattendance', models.IntegerField(default=0)),
                ('nb_of_section', models.IntegerField(default=0)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('education_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationYear', verbose_name='\u0627\u0644\u0633\u0646\u0629 \u0627\u0644\u062f\u0631\u0627\u0633\u064a\u0629')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='\u0627\u0646\u0634\u0623 \u0645\u0646 \u0642\u0628\u0644')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School', verbose_name='\u0627\u0644\u0645\u062f\u0631\u0633\u0629')),
            ],
            options={
                'abstract': False,
            },
        ),
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
            model_name='staffenroll',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='main record'),
        ),
        migrations.AddField(
            model_name='staffenroll',
            name='worklist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffenroll.Worklist', verbose_name='List of work'),
        ),
    ]