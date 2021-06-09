# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import Outreach


class OutreachTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/outreach-edit/', 'programme': 'Outreach'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-outreach/', 'programme': 'Outreach'})

    class Meta:
        model = Outreach
        fields = (
            'edit_column',
            'delete_column',
            'first_attendance_date',
            'governorate',
            'district',
            'internal_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )
