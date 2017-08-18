# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import Outreach


class BootstrapTable(tables.Table):

    class Meta:
        model = Outreach
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
        fields = (
            'edit_column',
            'delete_column',
            'school',
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


class PreTestTable(CommonTable):

    class Meta:
        model = Outreach
        fields = (
            'edit_column',
            'delete_column',
            'school',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'level',
            'assigned_to_level',
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


class PostTestTable(CommonTable):

    class Meta:
        model = Outreach
        fields = (
            'edit_column',
            'delete_column',
            'school',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'level',
            'assigned_to_level',
            'pre_test_total',
            'pre_test_result',
            'post_test_total',
            'post_test_result',
            'current_level',
            'current_section',
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


class SchoolTable(tables.Table):

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
    post_test_result = tables.Column(verbose_name=_('Post-test result'), accessor='refer_to_level')
    current_level = tables.Column(verbose_name=_('Current Level'), accessor='registered_in_level')
    current_section = tables.Column(verbose_name=_('Current Section'), accessor='section')

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
            'last_education_level',
            'last_education_year',
            'participated_in_alp',
            'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
        )
