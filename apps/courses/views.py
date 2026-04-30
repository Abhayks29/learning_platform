from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.utils import timezone

from .models import Course, Lesson, Enrollment, LessonProgress, Category
from .forms import CourseForm, LessonForm
from apps.users.decorators import role_required
from apps.courses.tasks import process_video_upload, send_enrollment_email


def course_list(request):
    courses = Course.objects.filter(status='published').select_related('teacher', 'category')
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '')

    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if search:
        courses = courses.filter(title__icontains=search)

    enrolled_ids = []
    if request.user.is_authenticated:
        enrolled_ids = list(
            Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
        )

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        'enrolled_ids': enrolled_ids,
        'selected_category': category_slug,
        'search': search,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    lessons = course.lessons.all()
    is_enrolled = False
    progress = {}

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if is_enrolled:
            for lp in LessonProgress.objects.filter(student=request.user, lesson__course=course):
                progress[lp.lesson_id] = lp.completed

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'progress': progress,
    })


@login_required
@role_required('student')
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        send_enrollment_email.delay(request.user.id, course.id)
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('course_detail', slug=slug)


@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if not lesson.is_free_preview:
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, 'Please enroll in this course to access this lesson.')
            return redirect('course_detail', slug=course_slug)

    progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
    lessons = course.lessons.all()
    lesson_ids = list(lessons.values_list('id', flat=True))
    current_idx = lesson_ids.index(lesson.id) if lesson.id in lesson_ids else 0
    next_lesson = lessons[current_idx + 1] if current_idx + 1 < len(lesson_ids) else None
    prev_lesson = lessons[current_idx - 1] if current_idx > 0 else None

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'progress': progress,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
    })


@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        total = lesson.course.lessons.count()
        completed = LessonProgress.objects.filter(
            student=request.user, lesson__course=lesson.course, completed=True
        ).count()
        if total > 0 and completed == total:
            Enrollment.objects.filter(student=request.user, course=lesson.course).update(completed=True)

        return JsonResponse({'status': 'ok', 'completed': True})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def update_watch_progress(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        seconds = int(request.POST.get('seconds', 0))
        progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
        progress.watched_seconds = max(progress.watched_seconds, seconds)
        progress.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


# --- Teacher views ---

@login_required
@role_required('teacher')
def teacher_course_list(request):
    courses = Course.objects.filter(teacher=request.user).annotate(
        enrollment_count=Count('enrollments')
    )
    return render(request, 'courses/teacher/course_list.html', {'courses': courses})


@login_required
@role_required('teacher')
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('teacher_course_detail', slug=course.slug)
    else:
        form = CourseForm()
    return render(request, 'courses/teacher/course_form.html', {'form': form, 'action': 'Create'})


@login_required
@role_required('teacher')
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('teacher_course_detail', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/teacher/course_form.html', {'form': form, 'course': course, 'action': 'Edit'})


@login_required
@role_required('teacher')
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('teacher_course_list')
    return render(request, 'courses/teacher/course_confirm_delete.html', {'course': course})


@login_required
@role_required('teacher')
def teacher_course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    lessons = course.lessons.all()
    enrollments = course.enrollments.select_related('student').annotate()
    return render(request, 'courses/teacher/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'enrollments': enrollments,
    })


@login_required
@role_required('teacher')
def lesson_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            if lesson.video:
                process_video_upload.delay(lesson.id)
            messages.success(request, 'Lesson added successfully.')
            return redirect('teacher_course_detail', slug=course_slug)
    else:
        next_order = course.lessons.count() + 1
        form = LessonForm(initial={'order': next_order})
    return render(request, 'courses/teacher/lesson_form.html', {'form': form, 'course': course, 'action': 'Add'})


@login_required
@role_required('teacher')
def lesson_edit(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated.')
            return redirect('teacher_course_detail', slug=course_slug)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/teacher/lesson_form.html', {'form': form, 'course': course, 'lesson': lesson, 'action': 'Edit'})


@login_required
@role_required('teacher')
def lesson_delete(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('teacher_course_detail', slug=course_slug)
    return render(request, 'courses/teacher/lesson_confirm_delete.html', {'lesson': lesson, 'course': course})


@login_required
@role_required('teacher')
def teacher_analytics(request):
    courses = Course.objects.filter(teacher=request.user).annotate(
        enrollment_count=Count('enrollments', distinct=True),
        avg_quiz_score=Avg('quizzes__attempts__score'),
    )
    return render(request, 'courses/teacher/analytics.html', {'courses': courses})
