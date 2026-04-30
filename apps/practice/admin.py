from django.contrib import admin
from .models import PracticeProblem, TestCase, CodeSubmission


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 2
    fields = ('input_data', 'expected_output', 'is_hidden')


@admin.register(PracticeProblem)
class PracticeProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'course', 'tags', 'created_at')
    list_filter = ('difficulty', 'course')
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TestCaseInline]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'input_data', 'expected_output', 'is_hidden')
    list_filter = ('is_hidden', 'problem')
    search_fields = ('problem__title',)


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'problem', 'language', 'status', 'runtime_ms', 'submitted_at')
    list_filter = ('status', 'language')
    search_fields = ('student__username', 'problem__title')
    raw_id_fields = ('student', 'problem')
    readonly_fields = ('submitted_at',)
