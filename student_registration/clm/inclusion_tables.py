# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import Inclusion


class InclusionTable(tables.Table):
    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/inclusion-edit/', 'programme': 'Inclusion'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_inclusion_delete_column.html',
                                          attrs={'url': '/clm/inclusion-delete/', 'programme': 'Inclusion'})

    followup_column = tables.TemplateColumn(verbose_name=_('followup'), orderable=False,
                                            template_name='django_tables2/clm_inclusion_followup_column.html',
                                            attrs={'url': '/clm/inclusion-followup/', 'programme': 'Inclusion'})

    # referral_column = tables.TemplateColumn(verbose_name=_('refer'), orderable=False,
    #                                         template_name='django_tables2/clm_referral_column.html',
    #                                         attrs={'url': '/clm/inclusion-referral/', 'programme': 'Inclusion'})
    # assessment_column = tables.TemplateColumn(verbose_name=_('Post-Assessment'), orderable=False,
    #                                                template_name='django_tables2/clm_assessment_column.html',
    #                                        attrs={'url': '/clm/inclusion-assessment/', 'programme': 'Inclusion'})

    class Meta:
        model = Inclusion
        fields = (
            'edit_column',
            'delete_column',
            'followup_column',
            'first_attendance_date',
            'round',
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
