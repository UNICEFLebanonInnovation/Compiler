# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import Registration


class BootstrapTable(tables.Table):

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    child_age = tables.Column(verbose_name=_('Age'), accessor='child.age')
    # created = tables.Column(verbose_name='Created', accessor='registration.created')
    child_birthday = tables.Column(verbose_name=_('Birthday'), accessor='child.birthday')

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap.html'
        fields = ()


class MainTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html')
    status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
                                          template_name='django_tables2/mscc/status_column.html')
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
                                       template_name='django_tables2/mscc/outreached_column.html')

    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')

    # center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    # governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    # caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    # cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'status_column',
            'type_column',
            'outreached',
            'absence_column',
            'round',
            'child.number',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'get_education_program',
            'class_section',
            'partner_unique_number',
            'has_previous_registration',
            # 'center',
            # 'center_type',
            # 'governorate',
            # 'caza',
            # 'cadaster',
            'owner',
            'modified_by',
        )

        def get_education_program(self, obj):
            return obj.education_program

        get_education_program.short_description = 'Education Program'


class FullTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html')
    status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
                                          template_name='django_tables2/mscc/status_column.html')
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
                                       template_name='django_tables2/mscc/outreached_column.html')
    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')
    center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')
    deleted = tables.Column(
        accessor='deleted',
        verbose_name='Deleted',
        orderable=True,
        empty_values=(),
        attrs={
            "td": {"class": "text-center"},
        },
        default="No"
    )

    def render_deleted(self, value):
        return "Yes" if value else "No"

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'status_column',
            'type_column',
            'outreached',
            'absence_column',
            'round',
            'child.number',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'education_program',
            'class_section',
            'partner_unique_number',
            'partner',
            'center',
            'center_type',
            'governorate',
            'caza',
            'cadaster',
            'has_previous_registration',
            'deleted',
            'owner',
            'modified_by'
        )


class PartnerTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html')
    status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
                                          template_name='django_tables2/mscc/status_column.html')
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
                                       template_name='django_tables2/mscc/outreached_column.html')
    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')
    center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'status_column',
            'type_column',
            'outreached',
            'absence_column',
            'round',
            'child.number',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'education_program',
            'class_section',
            'partner_unique_number',
            'center',
            'center_type',
            'governorate',
            'caza',
            'cadaster',
            'has_previous_registration',
            'owner',
            'modified_by'
        )


class YouthMainTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html')
    class Meta:
        model = Registration
        fields = (
            'action_column',
            'child.number',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            # 'center',
            # 'center_type',
            # 'governorate',
            # 'caza',
            # 'cadaster',
        )
