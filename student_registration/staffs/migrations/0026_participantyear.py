# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2020-04-03 18:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0025_auto_20200403_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participantyear', models.CharField(blank=True, choices=[('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020'), ('2020/2021', '2020/2021')], max_length=9, null=True)),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='staffs.Staffs', verbose_name='\u0627\u0644\u0639\u0627\u0645\u0644')),
            ],
        ),
    ]
