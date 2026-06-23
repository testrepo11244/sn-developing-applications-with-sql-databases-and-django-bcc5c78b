from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Submit answers for a given course exam
    path("<int:course_id>/submit/", views.submit, name="submit"),
    # Show the result of a specific submission
    path(
        "submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]