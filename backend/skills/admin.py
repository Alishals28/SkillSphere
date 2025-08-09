from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from .models import Skill, SkillCategory


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    """Enhanced admin interface for SkillCategory model"""
    
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Skill model"""
    
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['created_at']
