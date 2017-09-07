# coding: utf-8
import django_tables2 as tables

from .models import Enrollment


class BootstrapTable(tables.Table):

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class EnrollmentTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name='Edit student',
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/enrollments/edit/'})
    delete_column = tables.TemplateColumn(verbose_name='Delete student',
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/enrollments/'})
    moved_column = tables.TemplateColumn(verbose_name='Student moved',
                                         template_name='django_tables2/moved_column.html')
    grading_term1 = tables.TemplateColumn(verbose_name='Grading Term 1',
                                         template_name='django_tables2/grading_term1_column.html')
    grading_term2 = tables.TemplateColumn(verbose_name='Grading Term 2',
                                         template_name='django_tables2/grading_term2_column.html')

    student_age = tables.Column(verbose_name='Age', accessor='student.age')
    student_birthday = tables.Column(verbose_name='Birthday', accessor='student.birthday')
    student_phone_number = tables.Column(verbose_name='Phone number', accessor='student.phone_number')
    student_registered_in_unhcr = tables.Column(verbose_name='Registered in UNHCR',
                                                accessor='student.registered_in_unhcr')

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'delete_column',
            'moved_column',
            'grading_term1',
            'grading_term2',
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
            'classroom',
            'section',
            'last_education_level',
            'last_school_type',
            'last_school_shift',
            'last_school',
            'last_education_year',
            'last_year_result',
            'participated_in_alp',
            'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
        )
