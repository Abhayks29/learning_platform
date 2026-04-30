import subprocess
import tempfile
import os
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count

from .models import PracticeProblem, TestCase, CodeSubmission
from .forms import PracticeProblemForm, TestCaseFormSet, CodeSubmissionForm
from apps.users.decorators import role_required


def problem_list(request):
    problems = PracticeProblem.objects.annotate(
        total_submissions=Count('submissions', distinct=True),
        accepted_count=Count('submissions', filter=Q(submissions__status='accepted'), distinct=True),
    )

    difficulty = request.GET.get('difficulty', '')
    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if search:
        problems = problems.filter(Q(title__icontains=search) | Q(tags__icontains=search))

    solved_ids = []
    attempted_ids = []
    if request.user.is_authenticated:
        solved_ids = list(
            CodeSubmission.objects.filter(student=request.user, status='accepted')
            .values_list('problem_id', flat=True).distinct()
        )
        attempted_ids = list(
            CodeSubmission.objects.filter(student=request.user)
            .values_list('problem_id', flat=True).distinct()
        )
        if status_filter == 'solved':
            problems = problems.filter(id__in=solved_ids)
        elif status_filter == 'attempted':
            problems = problems.filter(id__in=attempted_ids).exclude(id__in=solved_ids)
        elif status_filter == 'unsolved':
            problems = problems.exclude(id__in=attempted_ids)

    return render(request, 'practice/problem_list.html', {
        'problems': problems,
        'solved_ids': solved_ids,
        'attempted_ids': attempted_ids,
        'difficulty': difficulty,
        'search': search,
        'status_filter': status_filter,
    })


@login_required
def problem_detail(request, slug):
    problem = get_object_or_404(PracticeProblem, slug=slug)
    visible_test_cases = problem.test_cases.filter(is_hidden=False)
    my_submissions = CodeSubmission.objects.filter(
        student=request.user, problem=problem
    ).order_by('-submitted_at')[:10]
    form = CodeSubmissionForm(initial={'code': problem.starter_code, 'language': 'python'})

    return render(request, 'practice/problem_detail.html', {
        'problem': problem,
        'test_cases': visible_test_cases,
        'my_submissions': my_submissions,
        'form': form,
    })


@login_required
@require_POST
def submit_code(request, slug):
    problem = get_object_or_404(PracticeProblem, slug=slug)
    form = CodeSubmissionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'status': 'error', 'message': 'Invalid form data'}, status=400)

    code = form.cleaned_data['code']
    language = form.cleaned_data['language']

    submission = CodeSubmission.objects.create(
        student=request.user,
        problem=problem,
        code=code,
        language=language,
        status=CodeSubmission.PENDING,
    )

    result = run_code_against_tests(code, language, problem)
    submission.status = result['status']
    submission.output = result['output']
    submission.runtime_ms = result.get('runtime_ms')
    submission.save()

    return JsonResponse({
        'status': submission.status,
        'output': submission.output,
        'runtime_ms': submission.runtime_ms,
        'submission_id': submission.id,
    })


@login_required
@require_POST
def run_code(request, slug):
    problem = get_object_or_404(PracticeProblem, slug=slug)
    code = request.POST.get('code', '')
    language = request.POST.get('language', 'python')
    test_cases = problem.test_cases.filter(is_hidden=False)
    result = run_code_against_tests(code, language, problem, test_cases_qs=test_cases)
    return JsonResponse(result)


def run_code_against_tests(code, language, problem, test_cases_qs=None):
    if test_cases_qs is None:
        test_cases_qs = problem.test_cases.all()

    if language != 'python':
        return {
            'status': CodeSubmission.ERROR,
            'output': f'Only Python execution is supported in this environment.',
            'runtime_ms': None,
        }

    results = []
    all_passed = True
    start = time.time()

    for tc in test_cases_qs:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.write(f'\n\nprint({tc.input_data})\n')
                fname = f.name

            proc = subprocess.run(
                ['python3', fname],
                capture_output=True, text=True, timeout=5
            )
            os.unlink(fname)

            actual = proc.stdout.strip()
            expected = tc.expected_output.strip()
            passed = actual == expected
            if not passed:
                all_passed = False

            results.append({
                'input': tc.input_data,
                'expected': expected,
                'actual': actual,
                'passed': passed,
                'error': proc.stderr[:200] if proc.stderr else '',
            })
        except subprocess.TimeoutExpired:
            all_passed = False
            results.append({'input': tc.input_data, 'passed': False, 'error': 'Time Limit Exceeded'})
        except Exception as e:
            all_passed = False
            results.append({'input': tc.input_data, 'passed': False, 'error': str(e)})

    runtime_ms = int((time.time() - start) * 1000)
    status = CodeSubmission.ACCEPTED if all_passed else CodeSubmission.WRONG
    output_lines = []
    for r in results:
        if r.get('passed'):
            output_lines.append(f"✓ Input: {r['input']}")
        else:
            output_lines.append(f"✗ Input: {r['input']} | Expected: {r.get('expected','')} | Got: {r.get('actual','')} {r.get('error','')}")

    return {'status': status, 'output': '\n'.join(output_lines), 'runtime_ms': runtime_ms, 'results': results}


# --- Teacher views ---

@login_required
@role_required('teacher', 'admin')
def teacher_problem_list(request):
    problems = PracticeProblem.objects.all()
    return render(request, 'practice/teacher/problem_list.html', {'problems': problems})


@login_required
@role_required('teacher', 'admin')
def problem_create(request):
    if request.method == 'POST':
        form = PracticeProblemForm(request.POST)
        formset = TestCaseFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            problem = form.save()
            formset.instance = problem
            formset.save()
            messages.success(request, 'Problem created successfully.')
            return redirect('problem_detail', slug=problem.slug)
    else:
        form = PracticeProblemForm()
        formset = TestCaseFormSet()
    return render(request, 'practice/teacher/problem_form.html', {'form': form, 'formset': formset})


@login_required
@role_required('teacher', 'admin')
def problem_edit(request, slug):
    problem = get_object_or_404(PracticeProblem, slug=slug)
    if request.method == 'POST':
        form = PracticeProblemForm(request.POST, instance=problem)
        formset = TestCaseFormSet(request.POST, instance=problem)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Problem updated.')
            return redirect('problem_detail', slug=problem.slug)
    else:
        form = PracticeProblemForm(instance=problem)
        formset = TestCaseFormSet(instance=problem)
    return render(request, 'practice/teacher/problem_form.html', {
        'form': form, 'formset': formset, 'problem': problem
    })
