from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll, name='enroll'),
    path('<slug:course_slug>/lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('lessons/<int:lesson_id>/progress/', views.update_watch_progress, name='update_watch_progress'),

    # Teacher
    path('teacher/courses/', views.teacher_course_list, name='teacher_course_list'),
    path('teacher/courses/create/', views.course_create, name='course_create'),
    path('teacher/courses/<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('teacher/courses/<slug:slug>/delete/', views.course_delete, name='course_delete'),
    path('teacher/courses/<slug:slug>/detail/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/courses/<slug:course_slug>/lessons/add/', views.lesson_create, name='lesson_create'),
    path('teacher/courses/<slug:course_slug>/lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('teacher/courses/<slug:course_slug>/lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('teacher/analytics/', views.teacher_analytics, name='teacher_analytics'),
]
