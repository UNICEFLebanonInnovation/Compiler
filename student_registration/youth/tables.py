# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import Registration, ProgramDocument


class RegistrationTable(tables.Table):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/youth/action_column.html')
    # status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
    #                                       template_name='django_tables2/youth/status_column.html')
    # outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
    #                                    template_name='django_tables2/youth/outreached_column.html')
    adolescent_disability = tables.Column(verbose_name=_('Disability'), accessor='adolescent.disability')

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            # 'status_column',
            # 'outreached',
            'adolescent.unicef_id',
            'adolescent.first_name',
            'adolescent.father_name',
            'adolescent.last_name',
            'adolescent.mother_fullname',
            'adolescent.gender',
            'adolescent_age',
            'adolescent.nationality',
            'adolescent_disability'
        )


class PDTable(tables.Table):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/youth/pd_action_column.html'
    )
    focal_point_name = tables.Column(verbose_name=_('UNICEF Focal Point'), accessor='focal_point.name')
    partner = tables.Column(verbose_name=_('Partner'), accessor='partner.short_name')
    type = tables.Column(verbose_name=_('Type'), accessor='project_type')
    sectors = tables.Column(verbose_name=_('Sectors'))
    governorate = tables.Column(accessor='get_governorate_names', verbose_name=_('Governorates'))
    population_groups = tables.Column(accessor='get_population_groups_name', verbose_name=_('Population Groups'))
    master_programs = tables.Column(accessor='get_master_program_names', verbose_name=_('Master Programs'))
    donor_names = tables.Column(accessor='get_donor_names', verbose_name=_('Donors'))
    budget = tables.Column(verbose_name=_('Budget'))

    class Meta:
        model = ProgramDocument
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'partner',
            'funded_by.name',
            'project_status.name',
            'project_code',
            'project_name',
            'implementing_partners',
            'focal_point_name',
            'start_date',
            'end_date',
            'plan',
            'sectors',
            'type',
            'governorate',
            'budget',
            'population_groups',
            'master_programs',
            'donor_names'
        )


class PDPartnerTable(tables.Table):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/youth/pd_action_column.html'
    )
    focal_point_name = tables.Column(verbose_name=_('UNICEF Focal Point'), accessor='focal_point.name')
    partner = tables.Column(verbose_name=_('Partner'), accessor='partner.short_name')
    type = tables.Column(verbose_name=_('Type'), accessor='project_type')
    sectors = tables.Column(verbose_name=_('Sectors'))
    governorate = tables.Column(accessor='get_governorate_names', verbose_name=_('Governorates'))
    population_groups = tables.Column(accessor='get_population_groups_name', verbose_name=_('Population Groups'))
    master_programs = tables.Column(accessor='get_master_program_names', verbose_name=_('Master Programs'))
    budget = tables.Column(verbose_name=_('Budget'))

    class Meta:
        model = ProgramDocument
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            'action_column',
            'partner',
            'funded_by.name',
            'project_status.name',
            'project_code',
            'project_name',
            'implementing_partners',
            'focal_point_name',
            'start_date',
            'end_date',
            'plan',
            'sectors',
            'type',
            'governorate',
            'budget',
            'population_groups',
            'master_programs',
        )
