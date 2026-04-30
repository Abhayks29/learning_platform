from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('problems/<slug:slug>/', views.problem_detail, name='problem_detail'),
    path('problems/<slug:slug>/submit/', views.submit_code, name='submit_code'),
    path('problems/<slug:slug>/run/', views.run_code, name='run_code'),

    # Teacher
    path('teacher/problems/', views.teacher_problem_list, name='teacher_problem_list'),
    path('teacher/problems/create/', views.problem_create, name='problem_create'),
    path('teacher/problems/<slug:slug>/edit/', views.problem_edit, name='problem_edit'),
]
