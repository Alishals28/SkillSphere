"""
Simple Badge Signals

Django signals to automatically check and award badges when users
complete activities.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from .services import BadgeService


@receiver(post_save, sender=Booking)
def check_badges_on_booking_completion(sender, instance, created, **kwargs):
    """Check and award badges when a booking is completed"""
    if instance.status == 'completed':
        # Check badges for both mentor and learner
        BadgeService.check_and_award_badges(instance.mentor)
        BadgeService.check_and_award_badges(instance.learner)
