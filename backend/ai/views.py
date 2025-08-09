from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import AIResponse, LearningPath, SkillAssessment, MentorRecommendation
from .services import AIService
from .serializers import (
    AIResponseSerializer,
    LearningPathSerializer,
    SkillAssessmentSerializer,
    MentorRecommendationSerializer,
    QuestionAnswerSerializer
)
from skills.models import Skill


class AIResponseListView(generics.ListAPIView):
    """
    List user's AI responses
    GET /api/ai/responses/
    """
    serializer_class = AIResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIResponse.objects.filter(user=self.request.user)
        
        # Filter by type
        response_type = self.request.query_params.get('type')
        if response_type:
            queryset = queryset.filter(type=response_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class AIResponseDetailView(generics.RetrieveAPIView):
    """
    Get specific AI response
    GET /api/ai/responses/{id}/
    """
    serializer_class = AIResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AIResponse.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_learning_recommendations(request):
    """
    Generate AI learning recommendations for user
    POST /api/ai/learning-recommendations/
    """
    skill_ids = request.data.get('skill_ids', [])
    skills = Skill.objects.filter(id__in=skill_ids) if skill_ids else None
    
    ai_response = AIService.generate_learning_recommendations(request.user, skills)
    
    serializer = AIResponseSerializer(ai_response)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_mentor_recommendations(request):
    """
    Generate AI mentor recommendations
    POST /api/ai/mentor-recommendations/
    """
    if request.user.role != 'learner':
        return Response(
            {'error': 'Only learners can get mentor recommendations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    skill_ids = request.data.get('skill_ids', [])
    limit = min(int(request.data.get('limit', 5)), 10)  # Max 10 recommendations
    
    target_skills = Skill.objects.filter(id__in=skill_ids) if skill_ids else None
    
    recommendations = AIService.generate_mentor_recommendations(
        request.user, target_skills, limit
    )
    
    serializer = MentorRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_mentor_recommendations(request):
    """
    Get existing mentor recommendations for learner
    GET /api/ai/mentor-recommendations/
    """
    if request.user.role != 'learner':
        return Response(
            {'error': 'Only learners can view mentor recommendations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    recommendations = MentorRecommendation.objects.filter(
        learner=request.user
    ).order_by('-match_score', '-created_at')
    
    serializer = MentorRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_mentor_recommendation(request, recommendation_id):
    """
    Rate a mentor recommendation
    POST /api/ai/mentor-recommendations/{id}/rate/
    """
    recommendation = get_object_or_404(
        MentorRecommendation,
        id=recommendation_id,
        learner=request.user
    )
    
    rating = request.data.get('rating')
    if not rating or not (1 <= int(rating) <= 5):
        return Response(
            {'error': 'Rating must be between 1 and 5'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    recommendation.user_rating = int(rating)
    recommendation.save()
    
    return Response({'message': 'Rating saved successfully'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ask_ai_question(request):
    """
    Ask AI a question about the platform or learning
    POST /api/ai/ask/
    """
    serializer = QuestionAnswerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    question = serializer.validated_data['question']
    context = serializer.validated_data.get('context', {})
    
    # Add user context
    context.update({
        'user_role': request.user.role,
        'user_name': request.user.full_name
    })
    
    ai_response = AIService.answer_question(question, context)
    ai_response.user = request.user
    ai_response.save()
    
    response_serializer = AIResponseSerializer(ai_response)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LearningPathListView(generics.ListCreateAPIView):
    """
    List user's learning paths or create new one
    GET/POST /api/ai/learning-paths/
    """
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'learner':
            return LearningPath.objects.filter(learner=self.request.user)
        else:
            # Mentors can see learning paths for learners they're mentoring
            return LearningPath.objects.filter(
                learner__learner_bookings__mentor=self.request.user
            ).distinct()
    
    def perform_create(self, serializer):
        if self.request.user.role != 'learner':
            raise permissions.PermissionDenied('Only learners can create learning paths')
        serializer.save(learner=self.request.user)


class LearningPathDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update specific learning path
    GET/PATCH /api/ai/learning-paths/{id}/
    """
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'learner':
            return LearningPath.objects.filter(learner=self.request.user)
        else:
            return LearningPath.objects.filter(
                learner__learner_bookings__mentor=self.request.user
            ).distinct()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_session_summary(request, session_id):
    """
    Generate AI summary for a session
    POST /api/ai/sessions/{id}/summary/
    """
    from mentoring_sessions.models import Session
    
    # Get session - only participants can generate summary
    if request.user.role == 'mentor':
        session = get_object_or_404(
            Session,
            id=session_id,
            booking__mentor=request.user,
            status='finished'
        )
    else:
        session = get_object_or_404(
            Session,
            id=session_id,
            booking__learner=request.user,
            status='finished'
        )
    
    # Check if summary already exists
    existing_summary = session.ai_responses.filter(type='session_summary').first()
    if existing_summary:
        serializer = AIResponseSerializer(existing_summary)
        return Response(serializer.data)
    
    # Generate new summary
    ai_response = AIService.generate_session_summary(session)
    
    serializer = AIResponseSerializer(ai_response)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class SkillAssessmentListView(generics.ListCreateAPIView):
    """
    List user's skill assessments
    GET /api/ai/skill-assessments/
    """
    serializer_class = SkillAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SkillAssessment.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_dashboard_stats(request):
    """
    Get AI usage statistics for user dashboard
    GET /api/ai/dashboard-stats/
    """
    user = request.user
    
    # AI responses stats
    total_responses = AIResponse.objects.filter(user=user).count()
    completed_responses = AIResponse.objects.filter(user=user, status='completed').count()
    
    # Learning recommendations
    learning_recommendations = AIResponse.objects.filter(
        user=user,
        type='learning_recommendation',
        status='completed'
    ).count()
    
    # Session summaries
    session_summaries = AIResponse.objects.filter(
        user=user,
        type='session_summary',
        status='completed'
    ).count()
    
    # Mentor recommendations (for learners)
    mentor_recommendations_count = 0
    if user.role == 'learner':
        mentor_recommendations_count = MentorRecommendation.objects.filter(
            learner=user
        ).count()
    
    # Learning paths
    learning_paths_count = 0
    if user.role == 'learner':
        learning_paths_count = LearningPath.objects.filter(learner=user).count()
    
    return Response({
        'total_ai_interactions': total_responses,
        'completed_ai_responses': completed_responses,
        'learning_recommendations': learning_recommendations,
        'session_summaries': session_summaries,
        'mentor_recommendations': mentor_recommendations_count,
        'learning_paths': learning_paths_count,
        'ai_features_available': {
            'learning_recommendations': True,
            'mentor_recommendations': user.role == 'learner',
            'session_summaries': True,
            'learning_paths': user.role == 'learner',
            'qa_assistant': True
        }
    })
