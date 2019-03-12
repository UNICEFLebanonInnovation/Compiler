# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-10 23:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0075_auto_20180405_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='last_informal_edu_year',
            field=models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018')], max_length=10, null=True, verbose_name='\u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0633\u0627\u0628\u0642\u0629 - \u0622\u062e\u0631 \u0633\u0646\u0629 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u063a\u064a\u0631 \u0627\u0644\u0646\u0638\u0627\u0645\u064a '),
        ),
    ]
