"""URL configuration for the Vanna integration UI."""

from django.urls import path

from .views import VannaConsoleView


app_name = "ai"


urlpatterns = [
    path("vanna/", VannaConsoleView.as_view(), name="vanna_console"),
]
