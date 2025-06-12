# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import Registration


class BootstrapTable(tables.Table):

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap4.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):
    child_age = tables.Column(verbose_name=_('Age'))
    child_birthday = tables.Column(verbose_name=_('Birthday'))
    education_program = tables.Column(verbose_name=_('Education Program'))
    class_section = tables.Column(verbose_name=_('Section'))
    has_previous_registration = tables.Column(verbose_name=_('Has Previous Registration'))

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap4.html'
        fields = ()

    def render_child_age(self, record):
        return record.child.age

    def render_child_birthday(self, record):
        return record.child.birthday

    def render_education_program(self, record):
        return record.education_program

    def render_class_section(self, record):
        return record.class_section

    def render_has_previous_registration(self, record):
        return record.has_previous_registration


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
            'child.unicef_id',
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
            'has_previous_registration',
            # 'center',
            # 'center_type',
            # 'governorate',
            # 'caza',
            # 'cadaster',
            'owner',
            'modified_by',
        )


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
            'child.unicef_id',
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
            'child.unicef_id',
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
            'child.unicef_id',
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
