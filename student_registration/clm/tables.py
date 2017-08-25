# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import CLM, BLN, RS, CBECE


class BootstrapTable(tables.Table):

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/enrollments/edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': 'api/alp/'})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')
    student_phone_number = tables.Column(verbose_name=_('Phone number'), accessor='student.phone_number')
    student_registered_in_unhcr = tables.Column(verbose_name=_('Registered in UNHCR'),
                                                accessor='student.registered_in_unhcr')

    pre_test_total = tables.Column(verbose_name=_('Pre-test total'), accessor='student.birthday')
    pre_test_result = tables.Column(verbose_name=_('Pre-test result'), accessor='assigned_to_level')
    post_test_total = tables.Column(verbose_name=_('Post-test total'), accessor='student.birthday')

    class Meta:
        model = CLM
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
            'pre_test_total',
            'pre_test_result',
            'post_test_total',
            'post_test_result',
            'current_level',
            'current_section',
            'student.nationality',
            'student.mother_fullname',
            'student.mother_nationality',
            'student_registered_in_unhcr',
            'student.id_type',
            'student.id_number',
            'student.address',
            'student_phone_number',
        )


class BLNTable(CommonTable):

    class Meta:
        model = BLN


class RSTable(CommonTable):

    class Meta:
        model = RS


class CBECETable(CommonTable):

    class Meta:
        model = CBECE
