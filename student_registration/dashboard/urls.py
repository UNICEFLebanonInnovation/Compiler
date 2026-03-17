from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'dashboard'

urlpatterns = [
    re_path(
        r'^chart-builder/$',
        view=views.ChartBuilderView.as_view(),
        name='chart_builder'
    ),
    re_path(
        r'^pivot-dashboard/$',
        view=views.PivotDashboardView.as_view(),
        name='pivot_dashboard'
    ),
    re_path(
        r'^pivot-data/$',
        view=views.pivot_data,
        name='pivot_data'
    ),
    re_path(
        r'^centers-map/$',
        view=views.CenterMapView.as_view(),
        name='centers_map'
    ),
    re_path(
        r'^center-map-data/$',
        view=views.center_map_data,
        name='center_map_data'
    ),
    re_path(
        r'^center-children-data/$',
        view=views.center_children_data,
        name='center_children_data'
    ),
]
