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
    # pre_assessment = tables.TemplateColumn(verbose_name=_('Pre-assessment'),
    #                                        template_name='django_tables2/clm_pre_assessment.html',
    #                                        attrs={'url': ''})
    # post_assessment = tables.TemplateColumn(verbose_name=_('Post-assessment'),
    #                                         template_name='django_tables2/clm_post_assessment.html',
    #                                         attrs={'url': ''})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'delete_column',
        )


class BLNTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/bln-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-bln/'})

    pre_assessment_result = tables.Column(verbose_name=_('Academic Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Academic Result - Post'), orderable=False,
                                           accessor='post_test_score')

    arabic_improvement = tables.Column(verbose_name=_('Arabic - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    english_improvement = tables.Column(verbose_name=_('English - Improvement'), orderable=False,
                                        accessor='english_improvement')
    french_improvement = tables.Column(verbose_name=_('French - Improvement'), orderable=False,
                                       accessor='french_improvement')
    foreign_language_improvement = tables.Column(verbose_name=_('Foreign language - Improvement'), orderable=False,
                                                 accessor='foreign_language_improvement')
    math_improvement = tables.Column(verbose_name=_('Math - Improvement'), orderable=False,
                                     accessor='math_improvement')

    assessment_improvement = tables.Column(verbose_name=_('Academic Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    class Meta:
        model = BLN
        fields = (
            'edit_column',
            'delete_column',
            'round',
            # 'cycle',
            'governorate',
            'district',
            'internal_number',
            'student.id_number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_assessment_result',
            'post_assessment_result',
            'arabic_improvement',
            'english_improvement',
            'french_improvement',
            'foreign_language_improvement',
            'math_improvement',
            'assessment_improvement',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class RSTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/rs-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-rs/'})

    #  Academic Result
    pre_test_total = tables.Column(verbose_name=_('Academic Result - Pre'), orderable=False,
                                   accessor='pretest_result')
    post_test_total = tables.Column(verbose_name=_('Academic Result - Post'), orderable=False,
                                    accessor='posttest_result')
    arabic_improvement = tables.Column(verbose_name=_('Arabic - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    language_improvement = tables.Column(verbose_name=_('Language - Improvement'), orderable=False,
                                         accessor='language_improvement')
    science_improvement = tables.Column(verbose_name=_('Science - Improvement'), orderable=False,
                                        accessor='science_improvement')
    math_improvement = tables.Column(verbose_name=_('Math - Improvement'), orderable=False,
                                     accessor='math_improvement')

    academic_test_improvement = tables.Column(verbose_name=_('Academic Result - Improvement'), orderable=False,
                                              accessor='academic_test_improvement')

    # Strategy Evaluation Result
    pre_assessment_result = tables.Column(verbose_name=_('Strategy Evaluation Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Strategy Evaluation Result - Post'), orderable=False,
                                           accessor='post_test_score')

    assessment_improvement = tables.Column(verbose_name=_('Strategy Evaluation Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    # Motivation Assessment Result
    pre_motivation_result = tables.Column(verbose_name=_('Motivation - Pre'), orderable=False,
                                          accessor='pre_motivation_score')
    post_motivation_result = tables.Column(verbose_name=_('Motivation - Post'), orderable=False,
                                           accessor='post_motivation_score')

    motivation_improvement = tables.Column(verbose_name=_('Motivation - Improvement'), orderable=False,
                                           accessor='motivation_improvement')

    # Self Assessment Result
    self_pre_assessment = tables.Column(verbose_name=_('Self Assessment - Pre'), orderable=False,
                                        accessor='pre_self_assessment_score')
    self_post_assessment = tables.Column(verbose_name=_('Self Assessment - Post'), orderable=False,
                                         accessor='post_self_assessment_score')

    self_assessment_improvement = tables.Column(verbose_name=_('Self Assessment - Improvement'), orderable=False,
                                                accessor='self_assessment_improvement')

    class Meta:
        model = RS
        fields = (
            'edit_column',
            'delete_column',
            'round',
            'type',
            'site',
            'school',
            'governorate',
            'district',
            'internal_number',
            'student.id_number',
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
            'section',
            'pre_test_total',
            'post_test_total',
            'arabic_improvement',
            'language_improvement',
            'science_improvement',
            'math_improvement',
            'academic_test_improvement',
            'pre_assessment_result',
            'post_assessment_result',
            'assessment_improvement',
            'pre_motivation_result',
            'post_motivation_result',
            'motivation_improvement',
            'self_pre_assessment',
            'self_post_assessment',
            'self_assessment_improvement',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class CBECETable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/edit_column.html',
                                        attrs={'url': '/clm/cbece-edit/'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-cbece/'})

    pre_assessment_result = tables.Column(verbose_name=_('Academic Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Academic Result - Post'), orderable=False,
                                           accessor='post_test_score')

    assessment_improvement = tables.Column(verbose_name=_('Academic Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    art_improvement = tables.Column(verbose_name=_('Language Art Domain - Improvement'), orderable=False,
                                    accessor='art_improvement')
    cognitive_improvement = tables.Column(verbose_name=_('Cognitive Domain - Improvement'), orderable=False,
                                        accessor='cognitive_improvement')
    science_improvement = tables.Column(verbose_name=_('Cognitive domain Science - Improvement'), orderable=False,
                                        accessor='science_improvement')
    social_improvement = tables.Column(verbose_name=_('Social Emotional Domain - Improvement'), orderable=False,
                                       accessor='social_improvement')
    psycho_improvement = tables.Column(verbose_name=_('Psychomotor Domain - Improvement'), orderable=False,
                                       accessor='psycho_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Domain - Improvement'), orderable=False,
                                         accessor='artistic_improvement')

    class Meta:
        model = CBECE
        fields = (
            'edit_column',
            'delete_column',
            'round',
            'cycle',
            'site',
            'school',
            'governorate',
            'district',
            'internal_number',
            'student.id_number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_assessment_result',
            'post_assessment_result',
            'assessment_improvement',
            'art_improvement',
            'science_improvement',
            'cognitive_improvement',
            'social_improvement',
            'psycho_improvement',
            'artistic_improvement',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )
