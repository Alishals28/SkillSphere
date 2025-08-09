from django.contrib import admin
from .models import (
    Review, ReviewTag, ReviewHelpful, ReviewReport,
    ReviewResponse, MentorRating, SkillRating, ReviewTemplate
)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reviewer', 'reviewee', 'overall_rating', 
        'review_type', 'is_approved', 'is_featured', 'created_at'
    ]
    list_filter = [
        'review_type', 'overall_rating', 'is_approved', 
        'is_featured', 'is_verified', 'would_recommend'
    ]
    search_fields = ['reviewer__email', 'reviewee__email', 'review_text']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count', 'reported_count']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reviewer', 'reviewee', 'booking', 'review_type')
        }),
        ('Ratings', {
            'fields': (
                'overall_rating', 'communication_rating', 'knowledge_rating',
                'punctuality_rating', 'professionalism_rating'
            )
        }),
        ('Content', {
            'fields': ('review_text', 'pros', 'cons', 'would_recommend', 'tags')
        }),
        ('Settings', {
            'fields': ('is_verified', 'is_anonymous', 'is_featured')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'moderation_notes', 'helpful_count', 'reported_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ReviewTag)
class ReviewTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'usage_count']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['usage_count']


@admin.register(MentorRating)
class MentorRatingAdmin(admin.ModelAdmin):
    list_display = [
        'mentor', 'overall_rating', 'total_reviews',
        'recommendation_percentage', 'last_review_date'
    ]
    search_fields = ['mentor__email', 'mentor__first_name', 'mentor__last_name']
    readonly_fields = [
        'overall_rating', 'total_reviews', 'communication_rating',
        'knowledge_rating', 'punctuality_rating', 'professionalism_rating',
        'five_star_count', 'four_star_count', 'three_star_count',
        'two_star_count', 'one_star_count', 'recommendation_count',
        'recommendation_percentage', 'last_review_date', 'updated_at'
    ]
    
    actions = ['update_ratings']
    
    def update_ratings(self, request, queryset):
        for rating in queryset:
            rating.update_ratings()
        self.message_user(request, f"Updated ratings for {queryset.count()} mentors")
    update_ratings.short_description = "Update mentor ratings"


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'review', 'reporter', 'reason', 
        'is_resolved', 'created_at'
    ]
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['reporter__email', 'description']
    readonly_fields = ['created_at', 'resolved_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('review', 'reporter', 'reason', 'description')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolution_notes', 'resolved_by', 'resolved_at')
        })
    )


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'responder', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['responder__email', 'response_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SkillRating)
class SkillRatingAdmin(admin.ModelAdmin):
    list_display = [
        'skill', 'mentor', 'expertise_rating', 
        'teaching_ability_rating', 'created_at'
    ]
    list_filter = ['skill', 'expertise_rating', 'teaching_ability_rating']
    search_fields = ['skill__name', 'mentor__email']
    readonly_fields = ['created_at']


@admin.register(ReviewTemplate)
class ReviewTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'review_type', 'is_active', 'usage_count', 'created_at']
    list_filter = ['review_type', 'is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['suggested_tags']
    readonly_fields = ['usage_count', 'created_at']


admin.site.register(ReviewHelpful)
