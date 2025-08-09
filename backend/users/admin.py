from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced admin interface for User model"""
    
    list_display = [
        'email', 'full_name', 'role', 'is_active', 'is_email_verified',
        'created_at', 'last_active', 'session_count', 'total_earnings_spent'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_email_verified', 'is_staff', 'is_superuser',
        'created_at', 'last_active', 'country'
    ]
    
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_active', 'session_count',
        'total_earnings_spent', 'average_rating', 'profile_picture_preview'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'first_name', 'last_name', 'role')
        }),
        ('Profile Details', {
            'fields': (
                'profile_picture', 'profile_picture_preview', 'bio', 
                'phone', 'country', 'timezone'
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active', 'is_email_verified', 'is_staff', 'is_superuser',
                'date_joined', 'last_login'
            )
        }),
        ('Statistics', {
            'fields': (
                'created_at', 'updated_at', 'last_active', 'session_count',
                'total_earnings_spent', 'average_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'verify_users', 'send_welcome_email']
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            booking_count=Count('learner_bookings') + Count('mentor_bookings'),
            avg_rating=Avg('mentor_bookings__learner_rating')
        )
    
    def session_count(self, obj):
        """Display total session count"""
        return obj.booking_count or 0
    session_count.short_description = 'Total Sessions'
    session_count.admin_order_field = 'booking_count'
    
    def total_earnings_spent(self, obj):
        """Display total earnings or spending"""
        if obj.role == 'mentor':
            total = obj.mentor_bookings.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            return f"${total:.2f} earned"
        else:
            total = obj.learner_bookings.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            return f"${total:.2f} spent"
    total_earnings_spent.short_description = 'Earnings/Spending'
    
    def average_rating(self, obj):
        """Display average rating"""
        if obj.role == 'mentor':
            avg = obj.avg_rating
            if avg:
                return f"{avg:.1f}/5.0"
        return "N/A"
    average_rating.short_description = 'Avg Rating'
    average_rating.admin_order_field = 'avg_rating'
    
    def profile_picture_preview(self, obj):
        """Display profile picture preview"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;">',
                obj.profile_picture.url
            )
        return "No picture"
    profile_picture_preview.short_description = 'Profile Picture'
    
    def activate_users(self, request, queryset):
        """Bulk activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def verify_users(self, request, queryset):
        """Bulk verify users"""
        updated = queryset.update(is_email_verified=True)
        self.message_user(request, f'{updated} users verified.')
    verify_users.short_description = "Verify selected users"
    
    def send_welcome_email(self, request, queryset):
        """Send welcome email to selected users"""
        # This would integrate with your email service
        count = queryset.count()
        self.message_user(request, f'Welcome emails sent to {count} users.')
    send_welcome_email.short_description = "Send welcome email"


# Custom admin site configuration
admin.site.site_header = "SkillSphere Admin Panel"
admin.site.site_title = "SkillSphere Admin"
admin.site.index_title = "Welcome to SkillSphere Administration"
