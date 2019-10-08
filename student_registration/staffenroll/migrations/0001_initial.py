# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-02 12:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0044_student_std_phone'),
        ('schools', '0039_auto_20190619_1028'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hourrate', models.IntegerField(blank=True, null=True, verbose_name='Hour Rate')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='StaffEnroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('joineddate', models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020'), ('2020/2021', '2020/2021'), ('2021/2022', '2021/2022'), ('2022/2023', '2022/2023'), ('2023/2024', '2023/2024'), ('2024/2025', '2024/2025'), ('2025/2026', '2025/2026'), ('2026/2027', '2026/2027'), ('2027/2028', '2027/2028'), ('2028/2029', '2028/2029'), ('2029/2030', '2029/2030'), ('2030/2031', '2030/2031'), ('2031/2032', '2031/2032'), ('2032/2033', '2032/2033'), ('2033/2034', '2033/2034'), ('2034/2035', '2034/2035'), ('2035/2036', '2035/2036'), ('2036/2037', '2036/2037'), ('2037/2038', '2037/2038'), ('2038/2039', '2038/2039'), ('2039/2040', '2039/2040'), ('2040/2041', '2040/2041'), ('2041/2042', '2041/2042'), ('2042/2043', '2042/2043'), ('2043/2044', '2043/2044'), ('2044/2045', '2044/2045'), ('2045/2046', '2045/2046'), ('2046/2047', '2046/2047'), ('2047/2048', '2047/2048'), ('2048/2049', '2048/2049'), ('na', 'N/A')], max_length=10, null=True)),
                ('first_education_year', models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020'), ('2020/2021', '2020/2021'), ('2021/2022', '2021/2022'), ('2022/2023', '2022/2023'), ('2023/2024', '2023/2024'), ('2024/2025', '2024/2025'), ('2025/2026', '2025/2026'), ('2026/2027', '2026/2027'), ('2027/2028', '2027/2028'), ('2028/2029', '2028/2029'), ('2029/2030', '2029/2030'), ('2030/2031', '2030/2031'), ('2031/2032', '2031/2032'), ('2032/2033', '2032/2033'), ('2033/2034', '2033/2034'), ('2034/2035', '2034/2035'), ('2035/2036', '2035/2036'), ('2036/2037', '2036/2037'), ('2037/2038', '2037/2038'), ('2038/2039', '2038/2039'), ('2039/2040', '2039/2040'), ('2040/2041', '2040/2041'), ('2041/2042', '2041/2042'), ('2042/2043', '2042/2043'), ('2043/2044', '2043/2044'), ('2044/2045', '2044/2045'), ('2045/2046', '2045/2046'), ('2046/2047', '2046/2047'), ('2047/2048', '2047/2048'), ('2048/2049', '2048/2049'), ('na', 'N/A')], max_length=10, null=True, verbose_name=' \u0622\u062e\u0631 \u0633\u0646\u0629 \u062f\u0631\u0627\u0633\u064a\u0629')),
                ('deleted', models.BooleanField(default=False, verbose_name='\u062d\u0630\u0641')),
                ('weeklyhours', models.IntegerField(default=0, verbose_name='Weekly Nb of hours')),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.ClassRoom', verbose_name='\u0627\u0644\u0635\u0641 \u0627\u0644\u062d\u0627\u0644\u064a')),
                ('education_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationYear', verbose_name='\u0627\u0644\u0633\u0646\u0629 \u0627\u0644\u062f\u0631\u0627\u0633\u064a\u0629')),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffenroll.Jobs', verbose_name='Jobs')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='\u0627\u0646\u0634\u0623 \u0645\u0646 \u0642\u0628\u0644')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school', to='schools.School', verbose_name='\u0627\u0644\u0645\u062f\u0631\u0633\u0629')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.Section', verbose_name='\u0627\u0644\u0634\u0639\u0628\u0629 \u0627\u0644\u062d\u0627\u0644\u064a\u0629')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_enrollment', to='students.Student')),
            ],
            options={
                'ordering': ['-student__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='staffenroll',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='staffenroll.Subjects', verbose_name='Subjects'),
        ),
    ]
