from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Quiz, Question, Choice, QuizAttempt, QuizAnswer
from .forms import QuizForm, QuestionForm, ChoiceFormSet
from apps.users.decorators import role_required
from apps.courses.models import Course


@login_required
@role_required('student')
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    already_attempted = QuizAttempt.objects.filter(
        student=request.user, quiz=quiz, completed_at__isnull=False
    ).exists()
    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'course': course,
        'already_attempted': already_attempted,
    })


@login_required
@role_required('student')
def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)
    return redirect('quiz_take', quiz_id=quiz_id, attempt_id=attempt.id)


@login_required
@role_required('student')
def quiz_take(request, quiz_id, attempt_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user, completed_at__isnull=True)
    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                try:
                    choice = Choice.objects.get(id=choice_id, question=question)
                    QuizAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=choice,
                        is_correct=choice.is_correct,
                    )
                except Choice.DoesNotExist:
                    pass

        score = attempt.calculate_score()
        attempt.score = score
        attempt.passed = score >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect('quiz_result', attempt_id=attempt.id)

    return render(request, 'quizzes/quiz_take.html', {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
    })


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    answers = attempt.answers.select_related('question', 'selected_choice').all()
    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'answers': answers,
        'quiz': attempt.quiz,
    })


# --- Teacher quiz management ---

@login_required
@role_required('teacher')
def teacher_quiz_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    quizzes = course.quizzes.all()
    return render(request, 'quizzes/teacher/quiz_list.html', {'course': course, 'quizzes': quizzes})


@login_required
@role_required('teacher')
def quiz_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Quiz created. Now add questions.')
            return redirect('quiz_builder', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quizzes/teacher/quiz_form.html', {'form': form, 'course': course})


@login_required
@role_required('teacher')
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated.')
            return redirect('quiz_builder', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizzes/teacher/quiz_form.html', {'form': form, 'quiz': quiz, 'course': quiz.course})


@login_required
@role_required('teacher')
def quiz_builder(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    questions = quiz.questions.prefetch_related('choices').all()
    return render(request, 'quizzes/teacher/quiz_builder.html', {'quiz': quiz, 'questions': questions})


@login_required
@role_required('teacher')
def question_add(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            formset = ChoiceFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
            messages.success(request, 'Question added.')
            return redirect('quiz_builder', quiz_id=quiz.id)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
    return render(request, 'quizzes/teacher/question_form.html', {
        'form': form, 'formset': formset, 'quiz': quiz
    })


@login_required
@role_required('teacher')
def question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__course__teacher=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Question updated.')
            return redirect('quiz_builder', quiz_id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)
    return render(request, 'quizzes/teacher/question_form.html', {
        'form': form, 'formset': formset, 'quiz': question.quiz, 'question': question
    })


@login_required
@role_required('teacher')
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__course__teacher=request.user)
    quiz_id = question.quiz.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('quiz_builder', quiz_id=quiz_id)
