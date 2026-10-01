from django.urls import path

from . import views

app_name = 'wellbeing'

urlpatterns = [
    path('', views.flag_list, name='flags'),
    path('flags/<int:pk>/follow-up/', views.follow_up, name='follow_up'),
    path('centres/', views.summaries, name='summaries'),
]
