from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Review, ReviewTag, MentorRating
from bookings.models import Booking
from skills.models import Skill, SkillCategory

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            email='mentor@test.com',
            password='testpass123',
            role='mentor'
        )
        self.learner = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            role='learner'
        )
        
        # Create skill and booking
        category = SkillCategory.objects.create(name='Programming')
        skill = Skill.objects.create(name='Python', category=category)
        
        self.booking = Booking.objects.create(
            learner=self.learner,
            mentor=self.mentor,
            primary_skill=skill,
            subject='Python Basics',
            duration_minutes=60,
            status='completed'
        )
    
    def test_review_creation(self):
        review = Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        self.assertEqual(review.reviewer, self.learner)
        self.assertEqual(review.reviewee, self.mentor)
        self.assertEqual(review.overall_rating, 5)
        self.assertTrue(review.is_approved)
    
    def test_mentor_rating_update(self):
        # Create initial rating
        mentor_rating = MentorRating.objects.create(mentor=self.mentor)
        
        # Create review
        Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        # Update ratings
        mentor_rating.update_ratings()
        mentor_rating.refresh_from_db()
        
        self.assertEqual(mentor_rating.overall_rating, 5.0)
        self.assertEqual(mentor_rating.total_reviews, 1)
        self.assertEqual(mentor_rating.five_star_count, 1)


class ReviewAPITest(APITestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            email='mentor@test.com',
            password='testpass123',
            role='mentor'
        )
        self.learner = User.objects.create_user(
            email='learner@test.com',
            password='testpass123',
            role='learner'
        )
        
        # Create skill and booking
        category = SkillCategory.objects.create(name='Programming')
        skill = Skill.objects.create(name='Python', category=category)
        
        self.booking = Booking.objects.create(
            learner=self.learner,
            mentor=self.mentor,
            primary_skill=skill,
            subject='Python Basics',
            duration_minutes=60,
            status='completed'
        )
        
        self.review_data = {
            'booking': self.booking.id,
            'reviewee': self.mentor.id,
            'review_type': 'mentor_review',
            'overall_rating': 5,
            'review_text': 'Excellent mentor!',
            'pros': 'Very knowledgeable',
            'cons': 'None',
            'would_recommend': True
        }
    
    def test_create_review(self):
        self.client.force_authenticate(user=self.learner)
        url = reverse('reviews:review-list')
        
        response = self.client.post(url, self.review_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        
        review = Review.objects.first()
        self.assertEqual(review.reviewer, self.learner)
        self.assertEqual(review.overall_rating, 5)
    
    def test_get_mentor_reviews(self):
        # Create a review
        Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        url = reverse('reviews:mentor-reviews', kwargs={'mentor_id': self.mentor.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_mentor_rating(self):
        # Create review and rating
        Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        url = reverse('reviews:mentor-rating', kwargs={'mentor_id': self.mentor.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_rating', response.data)
    
    def test_mark_review_helpful(self):
        # Create review
        review = Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        self.client.force_authenticate(user=self.mentor)
        url = reverse('reviews:review-mark-helpful', kwargs={'pk': review.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'added')
        
        review.refresh_from_db()
        self.assertEqual(review.helpful_count, 1)
    
    def test_duplicate_review_prevention(self):
        # Create first review
        Review.objects.create(
            reviewer=self.learner,
            reviewee=self.mentor,
            booking=self.booking,
            review_type='mentor_review',
            overall_rating=5,
            review_text='Great mentor!'
        )
        
        # Try to create duplicate
        self.client.force_authenticate(user=self.learner)
        url = reverse('reviews:review-list')
        
        response = self.client.post(url, self.review_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)
    
    def test_review_permissions(self):
        # Test that only participants can review
        other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            role='learner'
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('reviews:review-list')
        
        response = self.client.post(url, self.review_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
