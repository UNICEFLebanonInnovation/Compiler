import django_tables2 as tables
from django.utils.translation import gettext as _

from student_registration.mscc.tables import MainTable


class TLSMainTable(MainTable):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/tls/action_column.html',
    )
