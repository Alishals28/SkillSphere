"""
Social auth pipeline for SkillSphere
Handles user creation and role assignment during social authentication
"""

def save_profile(backend, user, response, *args, **kwargs):
    """
    Custom pipeline step to save additional profile data from social auth
    """
    if user:
        # Set default role if not set
        if not user.role:
            user.role = 'learner'
        
        # Mark email as verified for social auth users
        user.is_email_verified = True
        
        # Save avatar from social auth
        if hasattr(user, 'social_profile'):
            social_profile = user.social_profile
        else:
            from .models import SocialProfile
            social_profile, created = SocialProfile.objects.get_or_create(
                user=user,
                provider=backend.name,
                defaults={
                    'social_id': response.get('id', ''),
                    'extra_data': response
                }
            )
        
        # Update avatar URL if available
        avatar_url = None
        if backend.name == 'google-oauth2':
            avatar_url = response.get('picture')
        elif backend.name == 'github':
            avatar_url = response.get('avatar_url')
        
        if avatar_url:
            social_profile.avatar_url = avatar_url
            social_profile.save()
        
        user.save()
    
    return {'user': user}
