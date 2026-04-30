from django.contrib import admin
from .models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_score', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    date_hierarchy = 'created_at'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'status', 'score', 'submitted_at', 'graded_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'assignment__title')
    raw_id_fields = ('student', 'assignment')
    date_hierarchy = 'submitted_at'
    readonly_fields = ('submitted_at',)
