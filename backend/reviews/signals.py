from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review, MentorRating


@receiver(post_save, sender=Review)
def update_mentor_rating_on_review_save(sender, instance, created, **kwargs):
    """
    Update mentor rating when a review is saved
    """
    if instance.review_type == 'mentor_review' and instance.is_approved:
        mentor_rating, created = MentorRating.objects.get_or_create(
            mentor=instance.reviewee
        )
        mentor_rating.update_ratings()


@receiver(post_delete, sender=Review)
def update_mentor_rating_on_review_delete(sender, instance, **kwargs):
    """
    Update mentor rating when a review is deleted
    """
    if instance.review_type == 'mentor_review':
        try:
            mentor_rating = MentorRating.objects.get(mentor=instance.reviewee)
            mentor_rating.update_ratings()
        except MentorRating.DoesNotExist:
            pass
