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

    student_age = tables.Column(verbose_name=_('Age'), accessor='child.age')
    created = tables.Column(verbose_name='Created', accessor='registration.created')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='child.birthday')

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
