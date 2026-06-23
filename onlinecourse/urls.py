from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path('submit/', views.submit, name='submit'),
    path('exam/result/', views.show_exam_result, name='show_exam_result'),
]