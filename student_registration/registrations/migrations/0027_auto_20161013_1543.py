# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-13 12:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
        ('registrations', '0026_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='last_class_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.ClassRoom'),
        ),
        migrations.AddField(
            model_name='registration',
            name='last_education_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schools.EducationLevel'),
        ),
        migrations.AddField(
            model_name='registration',
            name='last_education_year',
            field=models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='last_year_result',
            field=models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d'), ('failed', '\u0645\u0639\u064a\u062f')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='result',
            field=models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d'), ('failed', '\u0645\u0639\u064a\u062f')], max_length=50, null=True),
        ),
    ]
