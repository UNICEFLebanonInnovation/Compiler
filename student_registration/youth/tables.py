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

    # adolescent_birthday = tables.Column(verbose_name=_('Birthday'), accessor='adolescent.birthday')

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap.html'
        fields = ()


class MainTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/youth/action_column.html')
    # status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
    #                                       template_name='django_tables2/youth/status_column.html')
    # outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
    #                                    template_name='django_tables2/youth/outreached_column.html')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            # 'status_column',
            # 'outreached',
            'adolescent.number',
            'adolescent.first_name',
            'adolescent.father_name',
            'adolescent.last_name',
            'adolescent.mother_fullname',
            'adolescent.gender',
            'adolescent_age',
            'adolescent.nationality',
        )


class FullTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/youth/action_column.html')
    # status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
    #                                       template_name='django_tables2/youth/status_column.html')
    # outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
    #                                    template_name='django_tables2/youth/outreached_column.html')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            # 'status_column',
            # 'outreached',
            'adolescent.number',
            'adolescent.first_name',
            'adolescent.father_name',
            'adolescent.last_name',
            'adolescent.mother_fullname',
            'adolescent.gender',
            'adolescent_age',
            'adolescent.nationality',
        )


class PartnerTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/youth/action_column.html')
    # status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
    #                                       template_name='django_tables2/youth/status_column.html')
    # outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
    #                                    template_name='django_tables2/youth/outreached_column.html')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            # 'status_column',
            # 'outreached',
            'adolescent.number',
            'adolescent.first_name',
            'adolescent.father_name',
            'adolescent.last_name',
            'adolescent.mother_fullname',
            'adolescent.gender',
            'adolescent_age',
            'adolescent.nationality',

        )


class YouthMainTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/youth/action_column.html')
    # status_column = tables.TemplateColumn(verbose_name=_('Status'), orderable=False,
    #                                       template_name='django_tables2/youth/status_column.html')
    # outreached = tables.TemplateColumn(verbose_name=_('Outreach Child?'), orderable=False,
    #                                    template_name='django_tables2/youth/outreached_column.html')
    class Meta:
        model = Registration
        fields = (
            'action_column',
            # 'status_column',
            # 'outreached',
            'adolescent.number',
            'adolescent.first_name',
            'adolescent.father_name',
            'adolescent.last_name',
            'adolescent.mother_fullname',
            'adolescent.gender',
            'adolescent_age',
            'adolescent_birthday',
            'adolescent.nationality',
        )
