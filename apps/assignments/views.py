from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm
from apps.users.decorators import role_required
from apps.courses.models import Course, Enrollment


@login_required
@role_required('student')
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    enrolled = Enrollment.objects.filter(student=request.user, course=assignment.course).exists()
    if not enrolled:
        messages.warning(request, 'You must be enrolled in this course to view assignments.')
        return redirect('course_detail', slug=assignment.course.slug)

    existing_submission = Submission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'submission': existing_submission,
    })


@login_required
@role_required('student')
def submission_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    enrolled = Enrollment.objects.filter(student=request.user, course=assignment.course).exists()
    if not enrolled:
        messages.warning(request, 'You must be enrolled in this course.')
        return redirect('course_list')

    existing = Submission.objects.filter(assignment=assignment, student=request.user).first()
    if existing:
        messages.info(request, 'You have already submitted this assignment.')
        return redirect('assignment_detail', assignment_id=assignment_id)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', assignment_id=assignment_id)
    else:
        form = SubmissionForm()
    return render(request, 'assignments/submission_form.html', {'form': form, 'assignment': assignment})


# --- Teacher views ---

@login_required
@role_required('teacher')
def teacher_assignment_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    assignments = course.assignments.all()
    return render(request, 'assignments/teacher/assignment_list.html', {
        'course': course, 'assignments': assignments
    })


@login_required
@role_required('teacher')
def assignment_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, 'Assignment created.')
            return redirect('teacher_assignment_list', course_slug=course_slug)
    else:
        form = AssignmentForm()
    return render(request, 'assignments/teacher/assignment_form.html', {'form': form, 'course': course})


@login_required
@role_required('teacher')
def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated.')
            return redirect('teacher_assignment_list', course_slug=assignment.course.slug)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'assignments/teacher/assignment_form.html', {
        'form': form, 'assignment': assignment, 'course': assignment.course
    })


@login_required
@role_required('teacher')
def submission_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    submissions = assignment.submissions.select_related('student').all()
    return render(request, 'assignments/teacher/submission_list.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
@role_required('teacher')
def grade_submission(request, submission_id):
    submission = get_object_or_404(
        Submission, id=submission_id, assignment__course__teacher=request.user
    )
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            graded = form.save(commit=False)
            graded.status = Submission.GRADED
            graded.graded_at = timezone.now()
            graded.save()
            messages.success(request, f'Submission graded: {graded.score}/{graded.assignment.max_score}')
            return redirect('submission_list', assignment_id=submission.assignment.id)
    else:
        form = GradeSubmissionForm(instance=submission)
    return render(request, 'assignments/teacher/grade_submission.html', {
        'form': form, 'submission': submission
    })
