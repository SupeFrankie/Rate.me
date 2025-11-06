from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Course, Feedback, Suggestion

class CustomAdminSite(admin.AdminSite):
    site_header = "Rate.me Control Panel"
    site_title = "Rate.me Admin"
    index_title = "Admin Dashboard"
    
    def each_context(self, request):
        request.session.set_expiry(600)
        return super().each_context(request)
    
custom_admin_site = CustomAdminSite(name='custom_admin') 

@admin.register(User, site=custom_admin_site) 
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'department')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_staff']
    list_filter = ['role', 'department', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


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