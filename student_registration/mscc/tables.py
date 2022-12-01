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
    created = tables.Column(verbose_name='Created', accessor='registration.created')
    child_birthday = tables.Column(verbose_name=_('Birthday'), accessor='child.birthday')

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap.html'
        fields = ()


class MainTable(CommonTable):
    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                          template_name='django_tables2/mscc/action_column.html',
                                          )

    class Meta:
        model = Registration
        fields = (
            'action_column',
            # 'delete_column',
            # 'monitoring_column',
            # 'referral_column',
            # 'followup_column',
            # 'round',
            # 'internal_number',
            # 'child.id_number',
            'child.number',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.sex',
            'child_age',
            'child_birthday',
            'child.nationality',
            'governorate',
            'district',
            'owner',
            'created',
            'modified_by',
            'modified',
        )
