# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import Center


class BootstrapTable(tables.Table):

    class Meta:
        model = Center
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CenterTable(tables.Table):
    edit_column = tables.TemplateColumn(verbose_name=_('Edit'), orderable=False,
                                        template_name='django_tables2/location/center_edit_column.html',
                                        attrs={'url': '/locations/Center-Edit/'})
    class Meta:
        model = Center
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'owner_name',
            'modified_by_name',)


