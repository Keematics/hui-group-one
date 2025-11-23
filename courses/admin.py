from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, GroupMember, ProfessionalCertification, Course,
    Module, ModuleProgress, CourseCertificate,
    ProfessionalCertificationCertificate
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'matric_number', 'title', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matric_number']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('matric_number', 'title', 'profile_picture')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('matric_number', 'title', 'profile_picture')}),
    )


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'matric_number', 'title', 'is_leader', 'order']
    list_filter = ['is_leader']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'matric_number']
    ordering = ['order', '-is_leader']


@admin.register(ProfessionalCertification)
class ProfessionalCertificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_total_courses', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'certification', 'order', 'get_total_modules', 'is_active', 'created_at']
    list_filter = ['certification', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'certification__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['certification', 'order', 'title']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'module_type', 'order', 'is_active', 'created_at']
    list_filter = ['module_type', 'course', 'is_active', 'created_at']
    search_fields = ['title', 'text_content', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['course', 'order', 'title']

    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'module_type', 'order', 'is_active')
        }),
        ('Content', {
            'fields': ('text_content', 'picture', 'video', 'video_duration')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'module',
        'is_completed',
        'video_watch_time',
        'get_progress_percentage',
        'last_accessed'
    ]
    list_filter = ['is_completed', 'module__module_type', 'last_accessed']
    search_fields = ['user__username', 'module__title', 'module__course__title']
    readonly_fields = ['started_at', 'last_accessed', 'completed_at']
    ordering = ['-last_accessed']

    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress_percentage.short_description = 'Progress'


@admin.register(CourseCertificate)
class CourseCertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'certificate_id', 'issued_at']
    list_filter = ['issued_at', 'course']
    search_fields = ['user__username', 'course__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']
    ordering = ['-issued_at']


@admin.register(ProfessionalCertificationCertificate)
class ProfessionalCertificationCertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'certification', 'certificate_id', 'issued_at']
    list_filter = ['issued_at', 'certification']
    search_fields = ['user__username', 'certification__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']
    ordering = ['-issued_at']
