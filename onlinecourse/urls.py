"""URL configuration for the onlinecourse app."""

from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    # Submit exam answers for a specific course
    path("<int:course_id>/submit/", views.submit, name="submit"),

    # Show the result of a particular submission
    path("submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
]