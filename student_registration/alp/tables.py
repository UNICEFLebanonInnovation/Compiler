# coding: utf-8
import django_tables2 as tables

from .models import Outreach


class BootstrapTable(tables.Table):

    class Meta:
        model = Outreach
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name='Edit student',
                                        template_name='django_tables2/edit_column.html')
    delete_column = tables.TemplateColumn(verbose_name='Delete student',
                                          template_name='django_tables2/delete_column.html')

    student_age = tables.Column(verbose_name='Age', accessor='student.age')
    student_birthday = tables.Column(verbose_name='Birthday', accessor='student.birthday')
    student_phone_number = tables.Column(verbose_name='Phone number', accessor='student.phone_number')
    student_registered_in_unhcr = tables.Column(verbose_name='Registered in UNHCR',
                                                accessor='student.registered_in_unhcr')

    class Meta:
        model = Outreach
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'delete_column',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'student.mother_nationality',
            'student_registered_in_unhcr',
            'student.id_type',
            'student.id_number',
            'student.address',
            'student_phone_number',
        )


class OutreachTable(CommonTable):

    class Meta:
        model = Outreach


class PreTestTable(CommonTable):

    class Meta:
        model = Outreach


class PostTestTable(CommonTable):

    class Meta:
        model = Outreach


class SchoolTable(CommonTable):

    class Meta:
        model = Outreach
