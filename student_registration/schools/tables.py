# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import School, Club, Meeting, CommunityInitiative, HealthVisit

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
    club_column = tables.TemplateColumn(verbose_name=_('Clubs'), orderable=False,
                                        template_name='django_tables2/school/club_list_column.html',
                                        attrs={'url': '/schools/club-list/', 'programme': 'Bridging'})

    meeting_column = tables.TemplateColumn(verbose_name=_('Meetings'), orderable=False,
                                        template_name='django_tables2/school/meeting_list_column.html',
                                        attrs={'url': '/schools/meeting-list/', 'programme': 'Bridging'})

    community_initiative_column = tables.TemplateColumn(verbose_name=_('Community Initiatives'), orderable=False,
                                        template_name='django_tables2/school/community_initiative_list_column.html',
                                        attrs={'url': '/schools/community-initiative-list/', 'programme': 'Bridging'})

    health_visit_column = tables.TemplateColumn(verbose_name=_('Health Visits'), orderable=False,
                                        template_name='django_tables2/school/health_visit_list_column.html',
                                        attrs={'url': '/schools/health-visit-list/', 'programme': 'Bridging'})

    bridging_export_column = tables.TemplateColumn(verbose_name=_('Dirasa Data'), orderable=False,
                                        template_name='django_tables2/school/bridging_export_column.html',
                                        attrs={'url': '/clm/bridging-school-export-data/', 'programme': 'Bridging'})

    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'), orderable=False,
    #                                       template_name='django_tables2/school_delete_column.html',
    #                                       attrs={'url': '/api/school/', 'programme': 'Bridging'})

    class Meta:
        model = School
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'club_column',
            'meeting_column',
            'community_initiative_column',
            'health_visit_column' ,
            'bridging_export_column',
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


class ClubTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit Club'), orderable=False,
                                        template_name='django_tables2/school/club_edit_column.html',
                                        attrs={'url': '/schools/club-edit/', 'programme': 'Bridging'})
    #
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete school'), orderable=False,
    #                                       template_name='django_tables2/school_delete_column.html',
    #                                       attrs={'url': '/api/school/', 'programme': 'Bridging'})

    class Meta:
        model = Club
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'club_name',
            'number_clubs',
            'club_type',
            'number_children',
            'owner',
            'modified_by',
            'created',
            'modified',
        )

class MeetingTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit Meeting'), orderable=False,
                                        template_name='django_tables2/school/meeting_edit_column.html',
                                        attrs={'url': '/schools/meeting-edit/', 'programme': 'Bridging'})

    class Meta:
        model = Meeting
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'meeting_name',
            'meeting_date',
            'number_participants',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class CommunityInitiativeTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit Meeting'), orderable=False,
                                        template_name='django_tables2/school/community_initiative_edit_column.html',
                                        attrs={'url': '/schools/community-initiative-edit/', 'programme': 'Bridging'})

    class Meta:
        model = CommunityInitiative
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'community_group_name',
            'number_initiatives',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class HealthVisitTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit Health Visit'), orderable=False,
                                        template_name='django_tables2/school/health_visit_edit_column.html',
                                        attrs={'url': '/schools/health-visit-edit/', 'programme': 'Bridging'})

    class Meta:
        model = HealthVisit
        template = 'django_tables2/bootstrap.html'
        fields = (
            'edit_column',
            'focal_point_name',
            'number_visits',
            'date_first_visit',
            'date_last_visit',
            'owner',
            'modified_by',
            'created',
            'modified',
        )
