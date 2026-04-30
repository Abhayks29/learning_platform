from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.timezone import localtime
from .models import User

admin.site.site_header = "EdTech Admin Panel"
admin.site.site_title = "EdTech Admin"
admin.site.index_title = "Platform Management"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'full_name', 'role_badge',
        'is_active_icon', 'date_joined', 'last_login', 'is_staff'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    list_per_page = 25
    readonly_fields = ('date_joined', 'last_login', 'created_at')
    actions = ['activate_users', 'deactivate_users', 'make_teacher', 'make_student']

    fieldsets = (
        ('Account', {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar', 'bio')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Activity', {'fields': ('date_joined', 'last_login', 'created_at'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or '—'
    full_name.short_description = 'Name'

    def role_badge(self, obj):
        colors = {
            'admin': '#dc2626',
            'teacher': '#d97706',
            'student': '#2563eb',
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#16a34a;font-weight:bold">✔ Active</span>')
        return format_html('<span style="color:#dc2626;font-weight:bold">✘ Inactive</span>')
    is_active_icon.short_description = 'Status'

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')

    @admin.action(description='Set role to Teacher')
    def make_teacher(self, request, queryset):
        updated = queryset.update(role=User.TEACHER)
        self.message_user(request, f'{updated} user(s) set as Teacher.')

    @admin.action(description='Set role to Student')
    def make_student(self, request, queryset):
        updated = queryset.update(role=User.STUDENT)
        self.message_user(request, f'{updated} user(s) set as Student.')
