# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import CLM, BLN, RS, CBECE


class BootstrapTable(tables.Table):

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': ''})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': ''})
    pre_assessment = tables.TemplateColumn(verbose_name=_('Pre-assessment'),
                                           template_name='django_tables2/clm_pre_assessment.html',
                                           attrs={'url': ''})
    post_assessment = tables.TemplateColumn(verbose_name=_('Post-assessment'),
                                            template_name='django_tables2/clm_post_assessment.html',
                                            attrs={'url': ''})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'delete_column',
            'pre_assessment',
            'post_assessment',
        )


class BLNTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/bln-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-bln/'})
    pre_assessment = tables.TemplateColumn(verbose_name=_('Pre-assessment'),
                                           template_name='django_tables2/clm_pre_assessment.html',
                                           attrs={'url': '/clm/bln-list/'})
    post_assessment = tables.TemplateColumn(verbose_name=_('Post-assessment'),
                                            template_name='django_tables2/clm_post_assessment.html',
                                            attrs={'url': '/clm/bln-list/'})

    class Meta:
        model = BLN
        fields = (
            'edit_column',
            'delete_column',
            'pre_assessment',
            'post_assessment',
            'cycle',
            'governorate',
            'district',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_test_score',
            'post_test_score',
            'participation',
            'learning_result',
        )


class RSTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/rs-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-bln/'})

    pre_test_total = tables.Column(verbose_name=_('Pre-test total'), orderable=False,
                                   accessor='pretest_result')
    post_test_total = tables.Column(verbose_name=_('Post-test total'), orderable=False,
                                    accessor='posttest_result')

    pre_assessment = tables.TemplateColumn(verbose_name=_('Pre-assessment'),
                                           template_name='django_tables2/clm_pre_assessment.html',
                                           attrs={'url': '/clm/rs-list/'})
    post_assessment = tables.TemplateColumn(verbose_name=_('Post-assessment'),
                                            template_name='django_tables2/clm_post_assessment.html',
                                            attrs={'url': '/clm/rs-list/'})

    class Meta:
        model = RS
        fields = (
            'edit_column',
            'delete_column',
            'pre_assessment',
            'post_assessment',
            'type',
            'site',
            'school',
            'governorate',
            'district',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'registered_in_school',
            'shift',
            'grade',
            'pre_test_total',
            'post_test_total',
            'pre_test_score',
            'post_test_score',
            'participation',
            'learning_result',
        )


class CBECETable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/cbece-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-cbece/'})
    pre_assessment = tables.TemplateColumn(verbose_name=_('Pre-assessment'),
                                           template_name='django_tables2/clm_pre_assessment.html',
                                           attrs={'url': '/clm/cbece-list/'})
    post_assessment = tables.TemplateColumn(verbose_name=_('Post-assessment'),
                                            template_name='django_tables2/clm_post_assessment.html',
                                            attrs={'url': '/clm/cbece-list/'})

    class Meta:
        model = CBECE
        fields = (
            'edit_column',
            'delete_column',
            'pre_assessment',
            'post_assessment',
            'cycle',
            'site',
            'school',
            'governorate',
            'district',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_test_score',
            'post_test_score',
            'participation',
            'learning_result',
        )
