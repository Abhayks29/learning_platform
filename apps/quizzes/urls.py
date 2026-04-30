from django.urls import path
from . import views

urlpatterns = [
    # Student
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('<int:quiz_id>/take/<int:attempt_id>/', views.quiz_take, name='quiz_take'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),

    # Teacher
    path('teacher/<slug:course_slug>/quizzes/', views.teacher_quiz_list, name='teacher_quiz_list'),
    path('teacher/<slug:course_slug>/quizzes/create/', views.quiz_create, name='quiz_create'),
    path('teacher/quiz/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('teacher/quiz/<int:quiz_id>/builder/', views.quiz_builder, name='quiz_builder'),
    path('teacher/quiz/<int:quiz_id>/questions/add/', views.question_add, name='question_add'),
    path('teacher/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('teacher/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
]
