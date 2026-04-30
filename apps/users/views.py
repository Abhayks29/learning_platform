from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q

from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from .decorators import role_required
from apps.courses.models import Course, Enrollment, LessonProgress
from apps.practice.models import CodeSubmission, PracticeProblem
from apps.quizzes.models import QuizAttempt


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    published_courses = Course.objects.filter(status='published').select_related('teacher', 'category')[:6]
    return render(request, 'home.html', {'courses': published_courses})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard_redirect')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_redirect(request):
    role = request.user.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')


@login_required
@role_required('admin')
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(status='published').count(),
        'pending_courses': Course.objects.filter(status='pending').count(),
        'total_enrollments': Enrollment.objects.count(),
        'recent_users': User.objects.order_by('-created_at')[:10],
        'recent_courses': Course.objects.order_by('-created_at')[:10],
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@role_required('teacher')
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user).annotate(
        enrollment_count=Count('enrollments')
    )
    context = {
        'courses': courses,
        'total_students': Enrollment.objects.filter(course__teacher=request.user).values('student').distinct().count(),
        'total_courses': courses.count(),
        'published_count': courses.filter(status='published').count(),
    }
    return render(request, 'courses/teacher/dashboard.html', context)


@login_required
@role_required('student')
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'course__teacher')
    solved_problems = CodeSubmission.objects.filter(
        student=request.user, status='accepted'
    ).values('problem').distinct().count()
    quiz_attempts = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False)
    avg_quiz_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0

    last_progress = LessonProgress.objects.filter(
        student=request.user, completed=False
    ).select_related('lesson__course').order_by('-lesson__id').first()

    context = {
        'enrollments': enrollments,
        'solved_count': solved_problems,
        'quiz_count': quiz_attempts.count(),
        'avg_quiz_score': round(avg_quiz_score, 1),
        'last_progress': last_progress,
        'completed_courses': enrollments.filter(completed=True).count(),
    }
    return render(request, 'users/student_dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


@login_required
def leaderboard(request):
    top_students = User.objects.filter(role='student').annotate(
        solved=Count(
            'code_submissions__problem',
            filter=Q(code_submissions__status='accepted'),
            distinct=True,
        )
    ).order_by('-solved')[:20]
    return render(request, 'users/leaderboard.html', {'top_students': top_students})
