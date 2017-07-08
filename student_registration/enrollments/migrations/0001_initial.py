# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-25 11:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0003_auto_20161021_1045'),
        ('locations', '0002_auto_20161002_2337'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0013_student_phone_prefix'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('relation_to_adult', models.CharField(blank=True, choices=[('child', '\u0627\u0628\u0646/\u0627\u0628\u0646\u0629'), ('grandchild', '\u062d\u0641\u064a\u062f'), ('nibling', '\u0627\u0628\u0646\u0629/\u0625\u0628\u0646 \u0623\u062e\u064a'), ('relative', '\u0623\u0642\u0627\u0631\u0628'), ('other', '\u0644\u064a\u0633 \u0645\u0646 \u0627\u0644\u0623\u0642\u0627\u0631\u0628')], max_length=50, null=True)),
                ('enrolled_last_year', models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('second', '\u0646\u0639\u0645 - \u0641\u064a \u062f\u0648\u0627\u0645 \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'), ('first', '\u0646\u0639\u0645 - \u0641\u064a \u062f\u0648\u0627\u0645 \u0627\u0644\u0635\u0628\u0627\u062d\u064a'), ('private', '\u0646\u0639\u0645 - \u0641\u064a \u0645\u062f\u0631\u0633\u0629 \u062e\u0627\u0635\u0629'), ('other', '\u0646\u0639\u0645 - \u0641\u064a \u0646\u0648\u0639 \u0622\u062e\u0631 \u0645\u0646 \u0627\u0644\u0645\u062f\u0627\u0631\u0633')], max_length=50, null=True)),
                ('year', models.CharField(blank=True, choices=[(b'2016', 2016), (b'2017', 2017), (b'2018', 2018), (b'2019', 2019), (b'2020', 2020), (b'2021', 2021), (b'2022', 2022), (b'2023', 2023), (b'2024', 2024), (b'2025', 2025), (b'2026', 2026), (b'2027', 2027), (b'2028', 2028), (b'2029', 2029), (b'2030', 2030), (b'2031', 2031), (b'2032', 2032), (b'2033', 2033), (b'2034', 2034), (b'2035', 2035), (b'2036', 2036), (b'2037', 2037), (b'2038', 2038), (b'2039', 2039), (b'2040', 2040), (b'2041', 2041), (b'2042', 2042), (b'2043', 2043), (b'2044', 2044), (b'2045', 2045), (b'2046', 2046), (b'2047', 2047), (b'2048', 2048), (b'2049', 2049), (b'2050', 2050)], max_length=4, null=True)),
                ('status', models.BooleanField(default=True)),
                ('out_of_school_two_years', models.BooleanField(default=False)),
                ('related_to_family', models.BooleanField(default=False)),
                ('enrolled_in_this_school', models.BooleanField(default=True)),
                ('registered_in_unhcr', models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True)),
                ('last_education_year', models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020')], max_length=10, null=True)),
                ('last_year_result', models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d'), ('failed', '\u0645\u0639\u064a\u062f')], max_length=50, null=True)),
                ('result', models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d'), ('failed', '\u0645\u0639\u064a\u062f')], max_length=50, null=True)),
                ('participated_in_alp', models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=50, null=True)),
                ('last_informal_edu_year', models.CharField(blank=True, choices=[('2000/2001', '2000/2001'), ('2001/2002', '2001/2002'), ('2002/2003', '2002/2003'), ('2003/2004', '2003/2004'), ('2004/2005', '2004/2005'), ('2005/2006', '2005/2006'), ('2006/2007', '2006/2007'), ('2007/2008', '2007/2008'), ('2008/2009', '2008/2009'), ('2009/2010', '2009/2010'), ('2010/2011', '2010/2011'), ('2011/2012', '2011/2012'), ('2012/2013', '2012/2013'), ('2013/2014', '2013/2014'), ('2014/2015', '2014/2015'), ('2015/2016', '2015/2016'), ('2016/2017', '2016/2017'), ('2017/2018', '2017/2018'), ('2018/2019', '2018/2019'), ('2019/2020', '2019/2020')], max_length=10, null=True)),
                ('last_informal_edu_result', models.CharField(blank=True, choices=[('graduated', '\u0646\u0627\u062c\u062d'), ('failed', '\u0645\u0639\u064a\u062f')], max_length=50, null=True)),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.ClassRoom')),
                ('enrolled_last_year_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='locations.Location')),
                ('enrolled_last_year_school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School')),
                ('grade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.Grade')),
                ('last_education_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.ClassRoom')),
                ('last_informal_edu_final_result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schools.ClassLevel')),
                ('last_informal_edu_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationLevel')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                # ('registering_adult', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='registrations.RegisteringAdult')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.Section')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='students.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
