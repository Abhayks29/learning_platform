from django.urls import path
from . import views

urlpatterns = [
    # Student
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('<int:assignment_id>/submit/', views.submission_create, name='submission_create'),

    # Teacher
    path('teacher/<slug:course_slug>/assignments/', views.teacher_assignment_list, name='teacher_assignment_list'),
    path('teacher/<slug:course_slug>/assignments/create/', views.assignment_create, name='assignment_create'),
    path('teacher/assignments/<int:assignment_id>/edit/', views.assignment_edit, name='assignment_edit'),
    path('teacher/assignments/<int:assignment_id>/submissions/', views.submission_list, name='submission_list'),
    path('teacher/submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]
