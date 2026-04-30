from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Course, Enrollment, Lesson, LessonProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'course_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def course_count(self, obj):
        return obj.course_set.count()
    course_count.short_description = 'Courses'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'category', 'status_badge', 'enrollment_count', 'lesson_count', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'teacher__username', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('teacher',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    actions = ['publish_courses', 'draft_courses']

    def status_badge(self, obj):
        colors = {'draft': '#6b7280', 'pending': '#d97706', 'published': '#16a34a'}
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrolled'

    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'

    @admin.action(description='Publish selected courses')
    def publish_courses(self, request, queryset):
        updated = queryset.update(status=Course.PUBLISHED)
        self.message_user(request, f'{updated} course(s) published.')

    @admin.action(description='Set selected courses to Draft')
    def draft_courses(self, request, queryset):
        updated = queryset.update(status=Course.DRAFT)
        self.message_user(request, f'{updated} course(s) set to draft.')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'completed', 'progress_percent')
    list_filter = ('completed', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    raw_id_fields = ('student', 'course')
    date_hierarchy = 'enrolled_at'
    list_per_page = 25

    def progress_percent(self, obj):
        pct = obj.get_progress_percent()
        color = '#16a34a' if pct == 100 else '#2563eb' if pct > 0 else '#6b7280'
        return format_html(
            '<span style="color:{};font-weight:600">{}%</span>', color, pct
        )
    progress_percent.short_description = 'Progress'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'is_free_preview')
    list_filter = ('is_free_preview', 'course')
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'watched_seconds', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('student__username', 'lesson__title')
    raw_id_fields = ('student', 'lesson')
