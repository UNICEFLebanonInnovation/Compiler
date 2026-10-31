from django.urls import path

from . import api

urlpatterns = [
    path('flags/', api.FlagsView.as_view(), name='wellbeing_flags_api'),
    path('flags/<int:pk>/follow-up/', api.FollowUpView.as_view(), name='wellbeing_follow_up_api'),
    path('summaries/', api.SummariesView.as_view(), name='wellbeing_summaries_api'),
    path('runs/', api.RunsView.as_view(), name='wellbeing_runs_api'),
    path('runs/<int:pk>/', api.RunView.as_view(), name='wellbeing_run_api'),
]
