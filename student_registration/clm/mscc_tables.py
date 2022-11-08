# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import CLM, MSCC


class BootstrapTable(tables.Table):

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    # edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
    #                                     template_name='django_tables2/edit_column.html',
    #                                     attrs={'url': ''})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
    #                                       template_name='django_tables2/delete_column.html',
    #                                       attrs={'url': ''})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    created = tables.Column(verbose_name='Created', accessor='clm.created')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        fields = (
            # 'edit_column',
            # 'delete_column',
        )


class MSCCTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html',
                                          )
    # student_number = tables.TemplateColumn(verbose_name=_('Number'), orderable=False,
    #                                        template_name='django_tables2/mscc/child_number.html',
    #                                        )

    # edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
    #                                     template_name='django_tables2/clm_edit_column.html',
    #                                     attrs={'url': '/clm/mscc-edit/', 'programme': 'MSCC'})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
    #                                       template_name='django_tables2/clm_delete_column.html',
    #                                       attrs={'url': '/api/clm-mscc/', 'programme': 'MSCC'})

    # education_column = tables.TemplateColumn(verbose_name=_('Education Situation'), orderable=False,
    #                                         template_name='django_tables2/mscc/education-situation_column.html',
    #                                         attrs={'url': '/clm/education-situation/', 'programme': 'MSCC'})
    #
    # diagnostic_assessment_column = tables.TemplateColumn(verbose_name=_('Diagnostic-Assessment'), orderable=False,
    #                                                template_name='django_tables2/mscc/diagnostic_assessment_column.html',
    #                                                attrs={'url': '/clm/diagnostic-assessment/', 'programme': 'MSCC'})
    #
    # education_assessment_column = tables.TemplateColumn(verbose_name=_('Education-Assessment'), orderable=False,
    #                                                template_name='django_tables2/mscc/education_assessment_column.html',
    #                                                attrs={'url': '/clm/education-assessment/', 'programme': 'MSCC'})

    class Meta:
        model = MSCC
        fields = (
            'action_column',
            # 'delete_column',
            # 'monitoring_column',
            # 'referral_column',
            # 'followup_column',
            # 'round',
            # 'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.mother_fullname',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'governorate',
            'district',
            'owner',
            'created',
            'modified_by',
            'modified',
        )


class MSCCYouthTable(CommonTable):
    action_column_youth = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column_youth.html',
                                          )
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
    #                                       template_name='django_tables2/clm_delete_column.html',
    #                                       attrs={'url': '/api/clm-mscc/', 'programme': 'MSCC'})

    class Meta:
        model = MSCC
        fields = (
            'action_column_youth',
            # 'delete_column',
            # 'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.mother_fullname',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'round',
            'governorate',
            'district',
            'owner',
            'created',
            'modified_by',
            'modified',
        )


class MSCCHealthTable(CommonTable):
    action_column_health = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column_health.html',
                                          )
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
    #                                       template_name='django_tables2/clm_delete_column.html',
    #                                       attrs={'url': '/api/clm-mscc/', 'programme': 'MSCC'})

    class Meta:
        model = MSCC
        fields = (
            'action_column_health',
            # 'delete_column',
            # 'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.mother_fullname',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'round',
            'governorate',
            'district',
            'owner',
            'created',
            'modified_by',
            'modified',
        )


class MSCCCPTable(CommonTable):
    action_column_cp = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column_cp.html',
                                          )
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-mscc/', 'programme': 'MSCC'})

    class Meta:
        model = MSCC
        fields = (
            'action_column_cp',
            'delete_column',
            'round',
            'governorate',
            'district',
            # 'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.mother_fullname',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


