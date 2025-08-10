#!/usr/bin/env python
"""
Script to create a test mentor user for testing the mentor dashboard
"""
import os
import sys
import django

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillsphere.settings')
django.setup()

from users.models import User

def create_test_mentor():
    """Create a test mentor user"""
    
    # Check if mentor already exists
    existing_mentor = User.objects.filter(email='mentor@test.com').first()
    if existing_mentor:
        print(f"Test mentor already exists: {existing_mentor.email}")
        print(f"Role: {existing_mentor.role}")
        return existing_mentor
    
    # Create new mentor
    mentor = User.objects.create_user(
        username='mentor_test',  # Add required username
        email='mentor@test.com',
        password='testpass123',
        first_name='Dr. Sarah',
        last_name='Johnson',
        role='mentor',
        is_mentor_approved=True,
        is_active=True
    )
    
    print(f"✅ Created test mentor: {mentor.email}")
    print(f"Name: {mentor.first_name} {mentor.last_name}")
    print(f"Role: {mentor.role}")
    print(f"Password: testpass123")
    
    return mentor

def create_test_learner():
    """Create a test learner user if not exists"""
    
    # Check if learner already exists
    existing_learner = User.objects.filter(email='learner@test.com').first()
    if existing_learner:
        print(f"Test learner already exists: {existing_learner.email}")
        return existing_learner
    
    # Create new learner
    learner = User.objects.create_user(
        username='learner_test',  # Add required username
        email='learner@test.com',
        password='testpass123',
        first_name='John',
        last_name='Smith',
        role='learner',
        is_active=True
    )
    
    print(f"✅ Created test learner: {learner.email}")
    print(f"Name: {learner.first_name} {learner.last_name}")
    print(f"Role: {learner.role}")
    print(f"Password: testpass123")
    
    return learner

if __name__ == '__main__':
    print("Creating test users for SkillSphere...")
    print("=" * 50)
    
    try:
        mentor = create_test_mentor()
        learner = create_test_learner()
        
        print("\n" + "=" * 50)
        print("✅ Test users created successfully!")
        print("\n📋 Test Credentials:")
        print("Mentor: mentor@test.com / testpass123")
        print("Learner: learner@test.com / testpass123")
        print("\n🚀 You can now test both dashboards!")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        sys.exit(1)
