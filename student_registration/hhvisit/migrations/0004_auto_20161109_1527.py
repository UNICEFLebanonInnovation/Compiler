# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-09 13:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hhvisit', '0003_auto_20161109_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdVisitTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254L)),
                ('first_enumerator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('second_enumerator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Specific Reason',
            },
        ),
        migrations.AddField(
            model_name='householdvisit',
            name='household_visit_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='hhvisit.HouseholdVisitTeam'),
        ),
    ]