# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import CLM, BLN, ABLN, RS, CBECE


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
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/bln-edit/', 'programme': 'BLN'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-bln/', 'programme': 'BLN'})
    arabic_improvement = tables.Column(verbose_name=_('Arabic Language Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    foreign_language_improvement = tables.Column(verbose_name=_('Foreign Language Development - Improvement'), orderable=False,
                                                 accessor='foreign_language_improvement')
    math_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                     accessor='math_improvement')
    social_emotional_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    psychomotor_improvement = tables.Column(verbose_name=_('Psychomotor Development for children with special needs - Improvement'),
                                       orderable=False, accessor='arabic_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
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
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'arabic_improvement',
            'foreign_language_improvement',
            'math_improvement',
            'social_emotional_improvement',
            'psychomotor_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class ABLNTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/abln-edit/', 'programme': 'ABLN'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-abln/', 'programme': 'ABLN'})
    arabic_improvement = tables.Column(verbose_name=_('Arabic Language Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    foreign_language_improvement = tables.Column(verbose_name=_('Foreign Language Development - Improvement'), orderable=False,
                                                 accessor='foreign_language_improvement')
    math_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                     accessor='math_improvement')
    social_emotional_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    psychomotor_improvement = tables.Column(verbose_name=_('Psychomotor Development for children with special needs - Improvement'),
                                       orderable=False, accessor='arabic_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    class Meta:
        model = ABLN
        fields = (
            'edit_column',
            'delete_column',
            'round',
            # 'cycle',
            'governorate',
            'district',
            'internal_number',
            'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'arabic_improvement',
            'foreign_language_improvement',
            'math_improvement',
            'social_emotional_improvement',
            'psychomotor_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
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
                                        attrs={'url': '/clm/rs-edit/', 'programme': 'RS'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/delete_column.html',
                                          attrs={'url': '/api/clm-rs/', 'programme': 'RS'})

    # Arabic reading result
    arabic_reading_improvement = tables.Column(verbose_name=_('Arabic Reading - Improvement'), orderable=False,
                                               accessor='arabic_reading_improvement')

    #  Academic Result
    pre_test_total = tables.Column(verbose_name=_('Assessment Result - Pre'), orderable=False,
                                   accessor='pretest_result')
    post_test_total = tables.Column(verbose_name=_('Assessment Result - Post'), orderable=False,
                                    accessor='posttest_result')
    arabic_improvement = tables.Column(verbose_name=_('Arabic - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    language_improvement = tables.Column(verbose_name=_('Language - Improvement'), orderable=False,
                                         accessor='language_improvement')
    science_improvement = tables.Column(verbose_name=_('Science - Improvement'), orderable=False,
                                        accessor='science_improvement')
    math_improvement = tables.Column(verbose_name=_('Math - Improvement'), orderable=False,
                                     accessor='math_improvement')

    academic_test_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
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
            'student.number',
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
            'pre_reading_score',
            'post_reading_score',
            'arabic_reading_improvement',
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
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
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
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/cbece-edit/', 'programme': 'CBECE'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-cbece/', 'programme': 'CBECE'})

    pre_assessment_result = tables.Column(verbose_name=_('Assessment Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Assessment Result - Post'), orderable=False,
                                           accessor='post_test_score')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    art_improvement = tables.Column(verbose_name=_('Language Development - Improvement'), orderable=False,
                                    accessor='art_improvement')
    cognitive_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                        accessor='cognitive_improvement')
    science_improvement = tables.Column(verbose_name=_('Cognitive Development - Science - Improvement'), orderable=False,
                                        accessor='science_improvement')
    social_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='social_improvement')
    psycho_improvement = tables.Column(verbose_name=_('Psychomotor Development - Improvement'), orderable=False,
                                       accessor='psycho_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
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
            'student.number',
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
            'final_grade',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )
