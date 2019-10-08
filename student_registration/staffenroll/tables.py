# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import StaffEnroll


class BootstrapTable(tables.Table):

    class Meta:
        model = StaffEnroll
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class StaffEnrollTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit Staff'), orderable=False,
                                        template_name='staffenroll/edit_column.html',
                                        attrs={'url': '/staffenroll/edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete Staff'), orderable=False,
                                          template_name='staffenroll/delete_column.html',
                                          attrs={'url': '/api/staffenroll/'})
    #student_age = tables.Column(verbose_name=_('Age'), accessor='student.age', orderable=False,)

    class Meta:
        model = StaffEnroll
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'delete_column',
            'staff.first_name',
            'staff.father_name',
            'staff.last_name',
            'staff.sex',
            'staff.mother_fullname',
            'staff.id_number',
            'staff.address',
            'staff_phone_number',
            'classroom',
            'section',
            'subject',
        )
