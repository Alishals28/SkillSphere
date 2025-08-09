from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404

from .models import Skill, SkillCategory, MentorSkill, MentorTag
from .serializers import (
    SkillSerializer, 
    SkillCategorySerializer,
    MentorSkillSerializer,
    MentorSkillCreateSerializer,
    MentorTagSerializer,
    MentorTagCreateSerializer,
    PopularSkillsSerializer,
    SkillStatisticsSerializer
)
from users.permissions import IsMentor, IsAdmin


class SkillCategoryListView(generics.ListAPIView):
    """
    List all skill categories
    GET /api/skills/categories/
    """
    queryset = SkillCategory.objects.all().order_by('name')
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.AllowAny]


class SkillCategoryDetailView(generics.RetrieveAPIView):
    """
    Get skill category details with related skills
    GET /api/skills/categories/{id}/
    """
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.AllowAny]


class SkillListCreateView(generics.ListCreateAPIView):
    """
    List all skills or create new skill (admin only)
    GET /api/skills/
    POST /api/skills/ (admin only)
    """
    serializer_class = SkillSerializer
    
    def get_queryset(self):
        queryset = Skill.objects.filter(is_active=True).select_related('category')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=category)
            else:
                queryset = queryset.filter(category__slug=category)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-popularity', 'name')
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a skill (admin only for modify)
    GET /api/skills/{id}/
    PUT/PATCH/DELETE /api/skills/{id}/ (admin only)
    """
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]


class MentorSkillListView(generics.ListCreateAPIView):
    """
    List mentor's skills or add new skill
    GET /api/mentors/me/skills/
    POST /api/mentors/me/skills/
    """
    serializer_class = MentorSkillSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return MentorSkill.objects.filter(
            mentor=self.request.user
        ).select_related('skill', 'skill__category').order_by('-is_primary', '-proficiency')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MentorSkillCreateSerializer
        return MentorSkillSerializer


class MentorSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a mentor skill
    GET/PUT/PATCH/DELETE /api/mentors/me/skills/{id}/
    """
    serializer_class = MentorSkillSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return MentorSkill.objects.filter(mentor=self.request.user)


class MentorTagListView(generics.ListCreateAPIView):
    """
    List mentor's tags or add new tag
    GET /api/mentors/me/tags/
    POST /api/mentors/me/tags/
    """
    serializer_class = MentorTagSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return MentorTag.objects.filter(mentor=self.request.user).order_by('tag')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MentorTagCreateSerializer
        return MentorTagSerializer


class MentorTagDetailView(generics.DestroyAPIView):
    """
    Delete a mentor tag
    DELETE /api/mentors/me/tags/{id}/
    """
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return MentorTag.objects.filter(mentor=self.request.user)


class SkillSearchView(APIView):
    """
    Search skills with filters
    GET /api/skills/search/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        is_active = request.GET.get('is_active', 'true')
        
        skills = Skill.objects.all()
        
        if query:
            skills = skills.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category:
            skills = skills.filter(category__slug=category)
        
        if is_active.lower() == 'true':
            skills = skills.filter(is_active=True)
        
        skills = skills.order_by('-popularity', 'name')
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)


class PopularSkillsView(APIView):
    """
    Get popular skills with statistics
    GET /api/skills/popular/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        
        skills = Skill.objects.filter(is_active=True).annotate(
            mentor_count=Count('mentor_skills__mentor', distinct=True),
            avg_rating=Avg('mentor_skills__mentor__mentor_bookings__learner_rating')
        ).order_by('-popularity', '-mentor_count')[:limit]
        
        data = []
        for skill in skills:
            data.append({
                'skill_id': skill.id,
                'skill_name': skill.name,
                'skill_slug': skill.slug,
                'mentor_count': skill.mentor_count or 0,
                'avg_rating': round(skill.avg_rating or 0, 1),
                'category_name': skill.category.name if skill.category else None,
                'popularity': skill.popularity
            })
        
        return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_skills(request):
    """
    Get popular skills with statistics
    GET /api/skills/popular/
    """
    limit = int(request.GET.get('limit', 10))
    
    skills = Skill.objects.filter(is_active=True).annotate(
        mentor_count=Count('mentor_skills', filter=Q(
            mentor_skills__mentor__is_mentor_approved=True,
            mentor_skills__mentor__role='mentor'
        )),
        avg_rating=Avg('mentor_skills__mentor__mentor_bookings__learner_rating', filter=Q(
            mentor_skills__mentor__mentor_bookings__status='completed'
        ))
    ).filter(mentor_count__gt=0).order_by('-mentor_count', '-avg_rating')[:limit]
    
    data = []
    for skill in skills:
        data.append({
            'skill_id': skill.id,
            'skill_name': skill.name,
            'skill_slug': skill.slug,
            'mentor_count': skill.mentor_count,
            'avg_rating': round(skill.avg_rating or 0, 1),
            'category_name': skill.category.name if skill.category else None
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def skill_statistics(request):
    """
    Get skill-related statistics
    GET /api/skills/statistics/
    """
    total_skills = Skill.objects.filter(is_active=True).count()
    total_categories = SkillCategory.objects.count()
    
    most_popular = Skill.objects.filter(is_active=True).order_by('-popularity').first()
    most_popular_name = most_popular.name if most_popular else "N/A"
    
    # Average skills per mentor
    from users.models import User
    mentors_with_skills = User.objects.filter(
        role='mentor',
        is_mentor_approved=True,
        mentor_skills__isnull=False
    ).annotate(skill_count=Count('mentor_skills')).aggregate(
        avg_skills=Avg('skill_count')
    )
    avg_skills_per_mentor = round(mentors_with_skills['avg_skills'] or 0, 1)
    
    data = {
        'total_skills': total_skills,
        'total_categories': total_categories,
        'most_popular_skill': most_popular_name,
        'avg_skills_per_mentor': avg_skills_per_mentor
    }
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsMentor])
def bulk_add_mentor_skills(request):
    """
    Bulk add skills to mentor profile
    POST /api/mentors/me/skills/bulk/
    """
    skill_ids = request.data.get('skill_ids', [])
    default_proficiency = request.data.get('default_proficiency', 3)
    
    if not skill_ids:
        return Response(
            {'error': 'skill_ids is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_skills = []
    errors = []
    
    for skill_id in skill_ids:
        try:
            skill = Skill.objects.get(id=skill_id, is_active=True)
            mentor_skill, created = MentorSkill.objects.get_or_create(
                mentor=request.user,
                skill=skill,
                defaults={'proficiency': default_proficiency}
            )
            
            if created:
                created_skills.append(MentorSkillSerializer(mentor_skill).data)
            else:
                errors.append(f"Skill '{skill.name}' already exists for this mentor")
        
        except Skill.DoesNotExist:
            errors.append(f"Skill with ID {skill_id} not found")
    
    return Response({
        'created_skills': created_skills,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_skills else status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_skills(request):
    """
    Search skills by name or description
    GET /api/skills/search/?q=python
    """
    query = request.GET.get('q', '')
    if not query:
        return Response([], status=status.HTTP_200_OK)
    
    skills = Skill.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).order_by('-popularity', 'name')[:20]
    
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)
