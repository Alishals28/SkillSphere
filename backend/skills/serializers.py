from rest_framework import serializers
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import Skill, SkillCategory, MentorSkill, MentorTag


class SkillCategorySerializer(serializers.ModelSerializer):
    """Serializer for skill categories"""
    skill_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'skill_count']
        read_only_fields = ['slug']

    def get_skill_count(self, obj):
        return obj.skills.filter(is_active=True).count()


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    mentor_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 
            'description', 'is_active', 'popularity', 'mentor_count'
        ]
        read_only_fields = ['slug', 'popularity']

    def get_mentor_count(self, obj):
        return obj.mentor_skills.filter(
            mentor__is_mentor_approved=True,
            mentor__role='mentor'
        ).count()


class MentorSkillSerializer(serializers.ModelSerializer):
    """Serializer for mentor skills"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_slug = serializers.CharField(source='skill.slug', read_only=True)
    skill_category = serializers.CharField(source='skill.category.name', read_only=True)
    
    class Meta:
        model = MentorSkill
        fields = [
            'id', 'skill', 'skill_name', 'skill_slug', 'skill_category',
            'proficiency', 'years_experience', 'is_primary'
        ]


class MentorSkillCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating mentor skills"""
    
    class Meta:
        model = MentorSkill
        fields = ['skill', 'proficiency', 'years_experience', 'is_primary']

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class MentorTagSerializer(serializers.ModelSerializer):
    """Serializer for mentor tags"""
    
    class Meta:
        model = MentorTag
        fields = ['id', 'tag']


class MentorTagCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating mentor tags"""
    
    class Meta:
        model = MentorTag
        fields = ['tag']

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class PopularSkillsSerializer(serializers.Serializer):
    """Serializer for popular skills with statistics"""
    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    skill_slug = serializers.CharField()
    mentor_count = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    category_name = serializers.CharField()


class SkillStatisticsSerializer(serializers.Serializer):
    """Serializer for skill-based statistics"""
    total_skills = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    most_popular_skill = serializers.CharField()
    avg_skills_per_mentor = serializers.FloatField()
