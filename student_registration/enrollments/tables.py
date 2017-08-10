# coding: utf-8
import django_tables2 as tables

from .models import Enrollment


class BootstrapTable(tables.Table):

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        # exclude = ('friendly', )


class EnrollmentTable(tables.Table):

    student = tables.RelatedLinkColumn()

    class Meta:
        model = Enrollment
        template = 'django_tables2/bootstrap.html'
        # sequence = (
        #     'student_fullname',
        #     'student__father_name',
        #     'student__last_name',
        # )
