from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserInterest

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')

        # Create test learners
        learner1 = User.objects.create_user(
            username='learner1',
            email='learner1@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role='learner',
            is_email_verified=True,
            bio='Enthusiastic learner looking to improve programming skills',
            learning_goals='Learn Python, Django, and web development',
            experience_level='beginner',
            timezone='America/New_York',
            country='US'
        )
        
        learner2 = User.objects.create_user(
            username='learner2',
            email='learner2@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role='learner',
            is_email_verified=True,
            bio='Data science enthusiast',
            learning_goals='Master machine learning and data analysis',
            experience_level='intermediate',
            timezone='Europe/London',
            country='GB'
        )

        # Add interests for learners
        UserInterest.objects.create(user=learner1, interest='Python')
        UserInterest.objects.create(user=learner1, interest='Web Development')
        UserInterest.objects.create(user=learner1, interest='Django')
        
        UserInterest.objects.create(user=learner2, interest='Machine Learning')
        UserInterest.objects.create(user=learner2, interest='Data Science')
        UserInterest.objects.create(user=learner2, interest='Python')

        # Create test mentors (pending approval)
        mentor1 = User.objects.create_user(
            username='mentor1',
            email='mentor1@test.com',
            password='testpass123',
            first_name='Alice',
            last_name='Johnson',
            role='mentor',
            is_email_verified=True,
            is_mentor_approved=False,  # Pending approval
            bio='Experienced software engineer',
            mentor_bio='Senior Python developer with 8+ years of experience in web development and system design. Passionate about teaching and helping others grow their technical skills.',
            teaching_experience='5 years of mentoring junior developers, conducted workshops on Python and Django',
            hourly_rate=75.00,
            portfolio_url='https://github.com/alice-johnson',
            linkedin_url='https://linkedin.com/in/alice-johnson',
            timezone='America/Los_Angeles',
            country='US'
        )

        mentor2 = User.objects.create_user(
            username='mentor2',
            email='mentor2@test.com',
            password='testpass123',
            first_name='Bob',
            last_name='Wilson',
            role='mentor',
            is_email_verified=True,
            is_mentor_approved=True,  # Already approved
            bio='AI/ML specialist and educator',
            mentor_bio='PhD in Computer Science with specialization in Machine Learning. 10+ years in industry working on AI projects. Love teaching complex concepts in simple terms.',
            teaching_experience='University lecturer for 3 years, industry mentor for 7 years',
            hourly_rate=100.00,
            portfolio_url='https://github.com/bob-wilson',
            linkedin_url='https://linkedin.com/in/bob-wilson',
            timezone='Europe/Berlin',
            country='DE',
            is_available=True
        )

        # Add interests for mentors
        UserInterest.objects.create(user=mentor1, interest='Python')
        UserInterest.objects.create(user=mentor1, interest='Django')
        UserInterest.objects.create(user=mentor1, interest='Web Development')
        UserInterest.objects.create(user=mentor1, interest='System Design')
        
        UserInterest.objects.create(user=mentor2, interest='Machine Learning')
        UserInterest.objects.create(user=mentor2, interest='Deep Learning')
        UserInterest.objects.create(user=mentor2, interest='Python')
        UserInterest.objects.create(user=mentor2, interest='TensorFlow')

        # Create another approved mentor
        mentor3 = User.objects.create_user(
            username='mentor3',
            email='mentor3@test.com',
            password='testpass123',
            first_name='Carol',
            last_name='Davis',
            role='mentor',
            is_email_verified=True,
            is_mentor_approved=True,
            bio='Frontend specialist and UX enthusiast',
            mentor_bio='Frontend developer with expertise in React, Vue.js, and modern JavaScript. Also experienced in UX/UI design principles.',
            teaching_experience='Led multiple coding bootcamps, mentored 50+ students',
            hourly_rate=80.00,
            portfolio_url='https://caroldavis.dev',
            linkedin_url='https://linkedin.com/in/carol-davis',
            timezone='America/Chicago',
            country='US',
            is_available=True
        )

        UserInterest.objects.create(user=mentor3, interest='JavaScript')
        UserInterest.objects.create(user=mentor3, interest='React')
        UserInterest.objects.create(user=mentor3, interest='Vue.js')
        UserInterest.objects.create(user=mentor3, interest='UX Design')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created test users:\n'
                f'✓ Learners: {learner1.email}, {learner2.email}\n'
                f'✓ Pending Mentor: {mentor1.email}\n'
                f'✓ Approved Mentors: {mentor2.email}, {mentor3.email}\n\n'
                f'All users have password: testpass123'
            )
        )
