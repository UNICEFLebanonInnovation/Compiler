from django.urls import re_path

from student_registration.mscc.views import get_file, main_mark_delete_view
from . import views

app_name = 'tls'

urlpatterns = [
    re_path(r'^child-add/$', view=views.TLSAddView.as_view(), name='child_add'),
    re_path(r'^child-edit/(?P<pk>[\w.@+-]+)/$', view=views.TLSEditView.as_view(), name='child_edit'),
    re_path(r'^child-mark-delete/(?P<pk>[\w.@+-]+)/$', view=main_mark_delete_view, name='child_mark_deleted'),
    re_path(r'^child-profile/(?P<pk>[\w.@+-]+)/$', view=views.TLSProfileView.as_view(), name='child_profile'),
    re_path(r'^list/$', view=views.TLSListView.as_view(), name='list'),
    re_path(r'^export-list-background/$', view=views.export_list_background, name='export_list_background'),
    re_path(r'^export-download/(?P<file_name>.+)/$', view=get_file, name='export_download'),
    re_path(r'^services/education-add/(?P<registry>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_add'),
    re_path(r'^services/education-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_edit'),
]
