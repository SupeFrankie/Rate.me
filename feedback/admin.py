from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Course, Feedback, Suggestion
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.contrib import messages



class CustomAdminSite(admin.AdminSite):
    site_header = "Rate.me Control Panel"
    site_title = "Rate.me Admin Portal"
    index_title = "Welcome to Rate.me Admin Control Center"
    
    def has_permission(self, request):
        """Only allow superusers or lecturer admins"""
        return request.user.is_active and (request.user.is_superuser or
                                           (request.user.is_staff and request.user.role == 'lecturer'))

    def each_context(self, request):
        request.session.set_expiry(600)
        return super().each_context(request)

# Create custom admin sites
admin_site = CustomAdminSite(name='admin')
custom_admin_site = CustomAdminSite(name='custom_admin')

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom user admin with role and department"""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'profile_picture', 'profile_preview')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'department', 'profile_picture')}),
    )
    list_display = ['username', 'profile_image_tag', 'email', 'first_name', 'last_name', 'role', 'department', 'is_staff']
    list_filter = ['role', 'department', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['profile_preview']
    
    def profile_image_tag(self, obj):
        """Display small profile picture in list view"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html('<div style="width: 40px; height: 40px; border-radius: 50%; background: #ddd; display: flex; align-items: center; justify-content: center;">👤</div>')
    
    profile_image_tag.short_description = 'Photo'
    
    def profile_preview(self, obj):
        """Display larger profile picture in edit form"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />',
                obj.profile_picture.url
            )
        return "No profile picture uploaded"
    
    profile_preview.short_description = 'Current Profile Picture'


@admin.register(Course, site=custom_admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'lecturer', 'department']
    list_filter = ['department', 'lecturer']
    search_fields = ['code', 'name', 'lecturer__username', 'lecturer__first_name', 'lecturer__last_name']
    ordering = ['code']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('lecturer')


@admin.register(Feedback, site=custom_admin_site)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'get_student_name',
        'lecturer',
        'course',
        'rating',
        'teaching_rating',
        'communication_rating',
        'engagement_rating',
        'is_anonymous',
        'created_at'
    ]
    list_filter = [
        'rating',
        'is_anonymous',
        'course__department',
        'lecturer'
    ]
    search_fields = [
        'student__username',
        'lecturer__username',
        'course__code',
        'course__name',
        'comment'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Participants', {
            'fields': ('student', 'lecturer', 'course')
        }),
        ('Ratings', {
            'fields': ('rating', 'teaching_rating', 'communication_rating', 'engagement_rating')
        }),
        ('Feedback', {
            'fields': ('comment', 'is_anonymous')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_student_name(self, obj):
        if obj.is_anonymous:
            return "Anonymous"
        return obj.student.get_full_name() or obj.student.username

    get_student_name.short_description = 'Student'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'lecturer', 'course')


@admin.register(Suggestion, site=custom_admin_site)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'lecturer',
        'based_on_feedback_count',
        'generated_at',
        'preview_suggestions'
    ]
    list_filter = ['lecturer']
    search_fields = [
        'lecturer__username',
        'lecturer__first_name',
        'lecturer__last_name',
        'suggestions_text'
    ]
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']

    fieldsets = (
        ('Lecturer Information', {
            'fields': ('lecturer', 'based_on_feedback_count')
        }),
        ('AI Suggestions', {
            'fields': ('suggestions_text',)
        }),
        ('Metadata', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )

    def preview_suggestions(self, obj):
        text = obj.suggestions_text or ""
        return text[:100] + "..." if len(text) > 100 else text

    preview_suggestions.short_description = 'Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('lecturer')