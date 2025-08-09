from rest_framework import serializers
from .models import AIResponse, LearningPath, LearningPathStep, SkillAssessment, MentorRecommendation
from skills.serializers import SkillSerializer
from users.serializers import UserSerializer


class AIResponseSerializer(serializers.ModelSerializer):
    """Serializer for AI responses"""
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = AIResponse
        fields = [
            'id', 'type', 'status', 'model_name', 'model_version',
            'prompt', 'response', 'tokens_used', 'processing_time_ms',
            'context_data', 'meta', 'error_message',
            'created_at', 'updated_at', 'completed_at', 'time_ago'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_at']
    
    def get_time_ago(self, obj):
        """Get human-readable time ago"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class LearningPathStepSerializer(serializers.ModelSerializer):
    """Serializer for learning path steps"""
    
    class Meta:
        model = LearningPathStep
        fields = [
            'id', 'title', 'description', 'order', 'step_type',
            'resources', 'estimated_duration_hours', 'is_completed',
            'completed_at', 'related_booking', 'created_at'
        ]
        read_only_fields = ['created_at']


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer for learning paths"""
    steps = LearningPathStepSerializer(many=True, read_only=True)
    target_skills = SkillSerializer(many=True, read_only=True)
    learner_name = serializers.CharField(source='learner.full_name', read_only=True)
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'description', 'difficulty_level',
            'estimated_duration_weeks', 'target_skills', 'is_active',
            'progress_percentage', 'steps', 'learner_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SkillAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for skill assessments"""
    skill = SkillSerializer(read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = SkillAssessment
        fields = [
            'id', 'skill', 'assessment_type', 'questions_data',
            'answers_data', 'proficiency_level', 'score_percentage',
            'strengths', 'weaknesses', 'recommendations',
            'user_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class MentorRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for mentor recommendations"""
    mentor = UserSerializer(read_only=True)
    matching_skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = MentorRecommendation
        fields = [
            'id', 'mentor', 'match_score', 'reasoning',
            'matching_skills', 'is_viewed', 'is_contacted',
            'user_rating', 'created_at'
        ]
        read_only_fields = ['created_at']


class QuestionAnswerSerializer(serializers.Serializer):
    """Serializer for Q&A requests"""
    question = serializers.CharField(max_length=1000)
    context = serializers.JSONField(required=False, default=dict)
    
    def validate_question(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Question must be at least 10 characters long")
        return value.strip()


class LearningPathCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating learning paths"""
    target_skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = LearningPath
        fields = [
            'title', 'description', 'difficulty_level',
            'estimated_duration_weeks', 'target_skill_ids'
        ]
    
    def create(self, validated_data):
        target_skill_ids = validated_data.pop('target_skill_ids', [])
        learning_path = LearningPath.objects.create(**validated_data)
        
        if target_skill_ids:
            from skills.models import Skill
            skills = Skill.objects.filter(id__in=target_skill_ids)
            learning_path.target_skills.set(skills)
        
        return learning_path


class SkillAssessmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating skill assessments"""
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SkillAssessment
        fields = [
            'skill_id', 'assessment_type', 'questions_data', 'answers_data'
        ]
    
    def create(self, validated_data):
        skill_id = validated_data.pop('skill_id')
        from skills.models import Skill
        skill = Skill.objects.get(id=skill_id)
        
        assessment = SkillAssessment.objects.create(
            skill=skill,
            **validated_data
        )
        return assessment


class AIInsightSerializer(serializers.Serializer):
    """Serializer for AI insights and analytics"""
    insight_type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    data = serializers.JSONField()
    confidence_score = serializers.FloatField()
    recommendations = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()


class AIConfigurationSerializer(serializers.Serializer):
    """Serializer for AI configuration settings"""
    model_name = serializers.CharField(default='gpt-3.5-turbo')
    temperature = serializers.FloatField(min_value=0, max_value=2, default=0.7)
    max_tokens = serializers.IntegerField(min_value=1, max_value=4000, default=1000)
    enable_session_summaries = serializers.BooleanField(default=True)
    enable_learning_recommendations = serializers.BooleanField(default=True)
    enable_mentor_matching = serializers.BooleanField(default=True)
