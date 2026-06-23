from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    # Lesson exam submission
    path("lesson/<int:lesson_id>/submit/", views.submit, name="submit"),
    # Result page for a particular submission
    path("submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
    # Additional example paths (not required for the task but typical)
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("lesson/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),
]