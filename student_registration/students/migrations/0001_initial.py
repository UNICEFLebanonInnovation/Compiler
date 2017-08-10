# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-19 08:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('first_name', models.CharField(blank=True, max_length=64, null=True)),
                ('last_name', models.CharField(blank=True, max_length=64, null=True)),
                ('father_name', models.CharField(blank=True, max_length=64, null=True)),
                ('full_name', models.CharField(blank=True, max_length=225, null=True)),
                ('mother_fullname', models.CharField(blank=True, max_length=64, null=True)),
                ('sex', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=50, null=True)),
                ('birthday_year', models.CharField(blank=True, choices=[(b'1990', 1990), (b'1991', 1991), (b'1992', 1992), (b'1993', 1993), (b'1994', 1994), (b'1995', 1995), (b'1996', 1996), (b'1997', 1997), (b'1998', 1998), (b'1999', 1999), (b'2000', 2000), (b'2001', 2001), (b'2002', 2002), (b'2003', 2003), (b'2004', 2004), (b'2005', 2005), (b'2006', 2006), (b'2007', 2007), (b'2008', 2008), (b'2009', 2009), (b'2010', 2010), (b'2011', 2011), (b'2012', 2012), (b'2013', 2013), (b'2014', 2014), (b'2015', 2015), (b'2016', 2016), (b'2017', 2017), (b'2018', 2018), (b'2019', 2019), (b'2020', 2020), (b'2021', 2021), (b'2022', 2022), (b'2023', 2023), (b'2024', 2024), (b'2025', 2025), (b'2026', 2026), (b'2027', 2027), (b'2028', 2028), (b'2029', 2029), (b'2030', 2030), (b'2031', 2031), (b'2032', 2032), (b'2033', 2033), (b'2034', 2034), (b'2035', 2035), (b'2036', 2036), (b'2037', 2037), (b'2038', 2038), (b'2039', 2039), (b'2040', 2040), (b'2041', 2041), (b'2042', 2042), (b'2043', 2043), (b'2044', 2044), (b'2045', 2045), (b'2046', 2046), (b'2047', 2047), (b'2048', 2048), (b'2049', 2049), (b'2050', 2050)], max_length=4, null=True)),
                ('birthday_month', models.CharField(blank=True, choices=[(b'1', 1), (b'2', 2), (b'3', 3), (b'4', 4), (b'5', 5), (b'6', 6), (b'7', 7), (b'8', 8), (b'9', 9), (b'10', 10), (b'11', 11), (b'12', 12)], max_length=2, null=True)),
                ('birthday_day', models.CharField(blank=True, choices=[(b'1', 1), (b'2', 2), (b'3', 3), (b'4', 4), (b'5', 5), (b'6', 6), (b'7', 7), (b'8', 8), (b'9', 9), (b'10', 10), (b'11', 11), (b'12', 12), (b'13', 13), (b'14', 14), (b'15', 15), (b'16', 16), (b'17', 17), (b'18', 18), (b'19', 19), (b'20', 20), (b'21', 21), (b'22', 22), (b'23', 23), (b'24', 24), (b'25', 25), (b'26', 26), (b'27', 27), (b'28', 28), (b'29', 29), (b'30', 30), (b'31', 31), (b'32', 32)], max_length=2, null=True)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('id_number', models.CharField(blank=True, max_length=45, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('nationality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.Nationality')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
