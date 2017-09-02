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
            'pretest_total',
            'assigned_to_level',
            'student_birthday',
            'student.nationality',
        )


class PostTestTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': ''})
    grading = tables.TemplateColumn(verbose_name=_('Grading'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/alp/post-test-grading/'})
    current_level = tables.Column(verbose_name=_('Current Level'), accessor='registered_in_level')
    current_section = tables.Column(verbose_name=_('Current Section'), accessor='section')

    class Meta:
        model = Outreach
        fields = (
            'edit_column',
            'delete_column',
            'grading',
            'school',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'level',
            'pretest_total',
            'assigned_to_level',
            'current_level',
            'current_section',
            'post_exam_result_arabic',
            'post_exam_language',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'posttest_total',
            'refer_to_level',
        )


class SchoolTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/enrollments/edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': 'api/alp/'})
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
            'level',
            'pretest_total',
            'assigned_to_level',
            'current_level',
            'current_section',
            'post_exam_result_arabic',
            'post_exam_language',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'posttest_total',
            'refer_to_level',
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
