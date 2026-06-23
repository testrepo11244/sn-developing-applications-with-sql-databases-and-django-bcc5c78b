from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    # Submit exam for a specific course
    path("<int:course_id>/submit/", views.submit, name="submit"),
    # Show result for a specific submission
    path("submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
]