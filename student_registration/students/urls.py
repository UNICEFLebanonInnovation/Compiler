from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the StudentListView
    # url(
    #     regex=r'^$',
    #     view=views.StudentListView.as_view(),
    #     name='list'
    # ),
    # url(regex=r'^student/test2/$', view=views.StudentList2View.as_view(), name='student_test2'),
    # url(regex=r'^student/list/$', view=views.StudentListJson.as_view(), name='student_list_json'),
    # url(regex=r'^student/listtest/$', view=views.StudentList2Json.as_view(), name='student_list2_json'),
    # url(regex=r'^student/update/$', view=views.update, name='student_update'),

    url(regex=r'^school/json-detail/$', view=views.SchoolDetailJson.as_view(), name='school_detail_json'),
]
