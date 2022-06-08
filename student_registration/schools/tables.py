# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import School

class BootstrapTable(tables.Table):

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}

class CommonTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit school'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': ''})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'),
    #                                       template_name='django_tables2/delete_column.html',
    #                                       attrs={'url': ''})

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            # 'delete_column',
        )


class SchoolTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit school'), orderable=False,
                                        template_name='django_tables2/school_edit_column.html',
                                        attrs={'url': '/schools/school-edit/', 'programme': 'Bridging'})
    #
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'), orderable=False,
    #                                       template_name='django_tables2/school_delete_column.html',
    #                                       attrs={'url': '/api/school/', 'programme': 'Bridging'})

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'governorate',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'owner',
            'modified_by',
            'created',
            'modified',
        )
