import openai
import json
import time
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional, Any
from .models import AIResponse, LearningPath, LearningPathStep, SkillAssessment, MentorRecommendation
import logging

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)


class AIService:
    """Service for AI integrations"""
    
    @staticmethod
    def create_ai_response(
        response_type: str,
        prompt: str,
        user=None,
        session=None,
        booking=None,
        context_data: Optional[Dict] = None,
        model_name: str = 'gpt-3.5-turbo'
    ) -> AIResponse:
        """Create an AI response record"""
        ai_response = AIResponse.objects.create(
            type=response_type,
            prompt=prompt,
            user=user,
            session=session,
            booking=booking,
            context_data=context_data or {},
            model_name=model_name,
            status='pending'
        )
        return ai_response
    
    @staticmethod
    def call_openai(
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Make a call to OpenAI API"""
        if not openai.api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'response': None,
                'tokens_used': 0,
                'processing_time_ms': 0
            }
        
        start_time = time.time()
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant for SkillSphere, a mentoring and learning platform. Provide helpful, accurate, and educational responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'success': True,
                'error': None,
                'response': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'processing_time_ms': processing_time_ms
            }
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"OpenAI API error: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'response': None,
                'tokens_used': 0,
                'processing_time_ms': processing_time_ms
            }
    
    @staticmethod
    def generate_session_summary(session) -> AIResponse:
        """Generate AI summary for a completed session"""
        booking = session.booking
        
        # Create context
        context_data = {
            'subject': booking.subject,
            'mentor_name': booking.mentor.full_name,
            'learner_name': booking.learner.full_name,
            'duration_minutes': session.duration_minutes,
            'skills': [skill.name for skill in booking.requested_skills.all()],
            'learner_notes': booking.learner_notes,
            'mentor_notes': booking.mentor_notes,
            'learner_feedback': booking.learner_feedback,
            'mentor_feedback': booking.mentor_feedback
        }
        
        # Create prompt
        prompt = f"""
        Please create a comprehensive summary of this mentoring session:
        
        Subject: {booking.subject}
        Mentor: {booking.mentor.full_name}
        Learner: {booking.learner.full_name}
        Duration: {session.duration_minutes} minutes
        Skills covered: {', '.join([skill.name for skill in booking.requested_skills.all()])}
        
        Learner's pre-session notes: {booking.learner_notes or 'None provided'}
        Mentor's session notes: {booking.mentor_notes or 'None provided'}
        Learner's feedback: {booking.learner_feedback or 'None provided'}
        Mentor's feedback: {booking.mentor_feedback or 'None provided'}
        
        Please provide:
        1. A brief summary of what was covered
        2. Key learning outcomes
        3. Areas where the learner showed progress
        4. Recommended next steps
        5. Suggested follow-up topics
        
        Format the response as a structured summary that would be useful for both the learner and mentor to reference.
        """
        
        # Create AI response record
        ai_response = AIService.create_ai_response(
            response_type='session_summary',
            prompt=prompt,
            session=session,
            booking=booking,
            context_data=context_data
        )
        
        # Make API call
        ai_response.status = 'processing'
        ai_response.save()
        
        result = AIService.call_openai(prompt)
        
        # Update response
        ai_response.status = 'completed' if result['success'] else 'failed'
        ai_response.response = result['response'] or ''
        ai_response.error_message = result['error'] or ''
        ai_response.tokens_used = result['tokens_used']
        ai_response.processing_time_ms = result['processing_time_ms']
        ai_response.completed_at = timezone.now()
        ai_response.save()
        
        return ai_response
    
    @staticmethod
    def generate_learning_recommendations(user, skills: List = None) -> AIResponse:
        """Generate personalized learning recommendations"""
        # Gather user context
        user_skills = []
        if hasattr(user, 'mentor_skills'):
            user_skills = [ms.skill.name for ms in user.mentor_skills.all()]
        
        recent_bookings = user.learner_bookings.filter(
            status='completed'
        ).order_by('-created_at')[:5]
        
        context_data = {
            'user_role': user.role,
            'current_skills': user_skills,
            'target_skills': [skill.name for skill in skills] if skills else [],
            'recent_sessions': [
                {
                    'subject': booking.subject,
                    'skills': [skill.name for skill in booking.requested_skills.all()],
                    'rating': booking.learner_rating
                }
                for booking in recent_bookings
            ]
        }
        
        target_skills_text = ', '.join([skill.name for skill in skills]) if skills else 'general skill development'
        
        prompt = f"""
        Please create personalized learning recommendations for this user:
        
        User Role: {user.role}
        Current Skills: {', '.join(user_skills) if user_skills else 'None specified'}
        Target Skills: {target_skills_text}
        
        Recent Learning Sessions:
        {chr(10).join([f"- {booking.subject} (Rating: {booking.learner_rating or 'N/A'})" for booking in recent_bookings]) or 'No recent sessions'}
        
        Please provide:
        1. 3-5 specific learning recommendations
        2. Suggested learning path or sequence
        3. Recommended session types (1-on-1 mentoring, group sessions, etc.)
        4. Estimated timeframe for each recommendation
        5. Prerequisite skills or knowledge needed
        
        Format as a practical, actionable learning plan.
        """
        
        ai_response = AIService.create_ai_response(
            response_type='learning_recommendation',
            prompt=prompt,
            user=user,
            context_data=context_data
        )
        
        ai_response.status = 'processing'
        ai_response.save()
        
        result = AIService.call_openai(prompt)
        
        ai_response.status = 'completed' if result['success'] else 'failed'
        ai_response.response = result['response'] or ''
        ai_response.error_message = result['error'] or ''
        ai_response.tokens_used = result['tokens_used']
        ai_response.processing_time_ms = result['processing_time_ms']
        ai_response.completed_at = timezone.now()
        ai_response.save()
        
        return ai_response
    
    @staticmethod
    def generate_mentor_recommendations(learner, target_skills: List = None, limit: int = 5) -> List[MentorRecommendation]:
        """Generate AI-powered mentor recommendations"""
        from users.models import User
        from skills.models import Skill
        
        # Get potential mentors
        mentors = User.objects.filter(
            role='mentor',
            is_mentor_approved=True,
            is_active=True
        ).prefetch_related('mentor_skills', 'mentor_skills__skill')
        
        if target_skills:
            # Filter mentors who have the target skills
            skill_ids = [skill.id for skill in target_skills]
            mentors = mentors.filter(
                mentor_skills__skill__id__in=skill_ids
            ).distinct()
        
        recommendations = []
        
        for mentor in mentors[:10]:  # Limit to top 10 for AI processing
            # Calculate basic compatibility
            mentor_skill_names = [ms.skill.name for ms in mentor.mentor_skills.all()]
            target_skill_names = [skill.name for skill in target_skills] if target_skills else []
            
            # Create AI prompt for mentor matching
            prompt = f"""
            Analyze the compatibility between this learner and mentor:
            
            Learner Profile:
            - Target Skills: {', '.join(target_skill_names) if target_skill_names else 'General learning'}
            - Role: Learner seeking mentorship
            
            Mentor Profile:
            - Name: {mentor.full_name}
            - Skills: {', '.join(mentor_skill_names)}
            - Rating: {mentor.mentor_rating or 'New mentor'}
            - Bio: {mentor.bio[:200] if mentor.bio else 'No bio available'}
            
            Please provide:
            1. A match score from 0.0 to 1.0 (1.0 being perfect match)
            2. A brief explanation of why this mentor is a good fit
            3. Key skills alignment
            4. Any potential concerns or limitations
            
            Respond in JSON format:
            {{
                "match_score": 0.0-1.0,
                "reasoning": "explanation",
                "key_alignments": ["skill1", "skill2"],
                "concerns": ["concern1", "concern2"]
            }}
            """
            
            ai_response = AIService.create_ai_response(
                response_type='mentor_match',
                prompt=prompt,
                user=learner,
                context_data={
                    'learner_id': learner.id,
                    'mentor_id': mentor.id,
                    'target_skills': target_skill_names
                }
            )
            
            ai_response.status = 'processing'
            ai_response.save()
            
            result = AIService.call_openai(prompt, temperature=0.3)  # Lower temperature for more consistent scoring
            
            ai_response.status = 'completed' if result['success'] else 'failed'
            ai_response.response = result['response'] or ''
            ai_response.error_message = result['error'] or ''
            ai_response.tokens_used = result['tokens_used']
            ai_response.processing_time_ms = result['processing_time_ms']
            ai_response.completed_at = timezone.now()
            ai_response.save()
            
            if result['success']:
                try:
                    # Parse AI response
                    ai_data = json.loads(result['response'])
                    match_score = float(ai_data.get('match_score', 0.5))
                    reasoning = ai_data.get('reasoning', 'AI-generated recommendation')
                    
                    # Create or update recommendation
                    recommendation, created = MentorRecommendation.objects.get_or_create(
                        learner=learner,
                        mentor=mentor,
                        defaults={
                            'ai_response': ai_response,
                            'match_score': match_score,
                            'reasoning': reasoning
                        }
                    )
                    
                    if not created:
                        recommendation.ai_response = ai_response
                        recommendation.match_score = match_score
                        recommendation.reasoning = reasoning
                        recommendation.save()
                    
                    # Add matching skills
                    if target_skills:
                        recommendation.matching_skills.set(target_skills)
                    
                    recommendations.append(recommendation)
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.error(f"Failed to parse AI recommendation response: {str(e)}")
                    # Fallback to basic scoring
                    basic_score = len(set(mentor_skill_names) & set(target_skill_names)) / max(len(target_skill_names), 1) if target_skill_names else 0.5
                    
                    recommendation, created = MentorRecommendation.objects.get_or_create(
                        learner=learner,
                        mentor=mentor,
                        defaults={
                            'ai_response': ai_response,
                            'match_score': basic_score,
                            'reasoning': 'Basic skill matching (AI parsing failed)'
                        }
                    )
                    
                    recommendations.append(recommendation)
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:limit]
    
    @staticmethod
    def answer_question(question: str, context: Dict = None) -> AIResponse:
        """Generate AI answer to user question"""
        context_text = ""
        if context:
            context_text = f"\nContext: {json.dumps(context, indent=2)}"
        
        prompt = f"""
        Please answer this question about SkillSphere mentoring platform:{context_text}
        
        Question: {question}
        
        Provide a helpful, accurate answer. If the question is about specific features or functionality of SkillSphere, 
        be specific about how our platform works. If you don't have enough information, be honest about that.
        """
        
        ai_response = AIService.create_ai_response(
            response_type='qa_response',
            prompt=prompt,
            context_data=context or {}
        )
        
        ai_response.status = 'processing'
        ai_response.save()
        
        result = AIService.call_openai(prompt)
        
        ai_response.status = 'completed' if result['success'] else 'failed'
        ai_response.response = result['response'] or ''
        ai_response.error_message = result['error'] or ''
        ai_response.tokens_used = result['tokens_used']
        ai_response.processing_time_ms = result['processing_time_ms']
        ai_response.completed_at = timezone.now()
        ai_response.save()
        
        return ai_response
