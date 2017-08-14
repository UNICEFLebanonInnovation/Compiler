# coding: utf-8
import django_tables2 as tables

from .models import Enrollment


class BootstrapTable(tables.Table):

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class EnrollmentTable(tables.Table):

    # student = tables.RelatedLinkColumn()
    id = tables.LinkColumn()

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        fields = (
            'id',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student.age',
            'student.birthday',
            'student.nationality',
            'student.mother_fullname',
            'student.mother_nationality',
            'student.registered_in_unhcr',
            'student.id_type',
            'student.id_number',
            'student.address',
            'student.phone_number',
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
