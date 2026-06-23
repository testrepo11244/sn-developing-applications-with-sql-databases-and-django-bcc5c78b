from django.urls import path
from . import views

urlpatterns = [
    # Submit an exam for a specific course
    path("<int:course_id>/submit/", views.submit, name="submit"),
    # Show the result of a specific submission
    path("submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
]