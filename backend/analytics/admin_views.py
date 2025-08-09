from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from bookings.models import Booking
from skills.models import Skill
from analytics.models import AnalyticsEvent, PlatformAnalytics
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

User = get_user_model()


@staff_member_required
def admin_dashboard(request):
    """
    Enhanced admin dashboard with comprehensive statistics
    """
    # Calculate date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # User statistics
    user_stats = {
        'total_users': User.objects.count(),
        'total_mentors': User.objects.filter(role='mentor').count(),
        'total_learners': User.objects.filter(role='learner').count(),
        'new_users_30d': User.objects.filter(created_at__gte=last_30_days).count(),
        'new_users_7d': User.objects.filter(created_at__gte=last_7_days).count(),
        'active_users_30d': User.objects.filter(last_active__gte=last_30_days).count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
    }
    
    # Session statistics
    session_stats = {
        'total_sessions': Booking.objects.count(),
        'completed_sessions': Booking.objects.filter(status='completed').count(),
        'pending_sessions': Booking.objects.filter(status='pending').count(),
        'cancelled_sessions': Booking.objects.filter(status='cancelled').count(),
        'sessions_30d': Booking.objects.filter(created_at__gte=last_30_days).count(),
        'sessions_7d': Booking.objects.filter(created_at__gte=last_7_days).count(),
    }
    
    # Financial statistics
    financial_stats = Booking.objects.filter(status='completed').aggregate(
        total_revenue=Sum('total_amount'),
        average_session_value=Avg('total_amount'),
        revenue_30d=Sum('total_amount', filter=Q(created_at__gte=last_30_days)),
        revenue_7d=Sum('total_amount', filter=Q(created_at__gte=last_7_days))
    )
    
    # Platform statistics
    platform_stats = {
        'total_skills': Skill.objects.count(),
        'active_skills': Skill.objects.filter(is_active=True).count(),
        'average_rating': Booking.objects.filter(
            status='completed', 
            learner_rating__isnull=False
        ).aggregate(avg=Avg('learner_rating'))['avg'] or 0,
    }
    
    # Top performing mentors
    top_mentors = User.objects.filter(role='mentor').annotate(
        session_count=Count('mentor_bookings', filter=Q(mentor_bookings__status='completed')),
        total_earnings=Sum('mentor_bookings__total_amount', filter=Q(mentor_bookings__status='completed')),
        avg_rating=Avg('mentor_bookings__learner_rating', filter=Q(mentor_bookings__status='completed'))
    ).filter(session_count__gt=0).order_by('-total_earnings')[:5]
    
    # Most popular skills
    popular_skills = Skill.objects.annotate(
        session_count=Count('booking_primary_skill'),
        revenue=Sum('booking_primary_skill__total_amount', filter=Q(booking_primary_skill__status='completed'))
    ).filter(session_count__gt=0).order_by('-session_count')[:5]
    
    # Recent activities
    recent_bookings = Booking.objects.select_related('learner', 'mentor').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-created_at')[:10]
    
    # Growth data for charts (last 30 days)
    growth_data = []
    for i in range(30):
        date = today - timedelta(days=i)
        day_data = {
            'date': date.strftime('%Y-%m-%d'),
            'new_users': User.objects.filter(created_at__date=date).count(),
            'new_sessions': Booking.objects.filter(created_at__date=date).count(),
            'revenue': Booking.objects.filter(
                created_at__date=date, 
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
        }
        growth_data.append(day_data)
    
    growth_data.reverse()  # Oldest to newest
    
    context = {
        'user_stats': user_stats,
        'session_stats': session_stats,
        'financial_stats': financial_stats,
        'platform_stats': platform_stats,
        'top_mentors': top_mentors,
        'popular_skills': popular_skills,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'growth_data': growth_data,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
@require_http_methods(["GET"])
def admin_analytics_api(request):
    """
    API endpoint for admin analytics data
    """
    period = request.GET.get('period', '30')  # days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))
    
    # User growth
    user_growth = User.objects.filter(
        created_at__gte=start_date
    ).extra({
        'date': 'date(created_at)'
    }).values('date').annotate(
        count=Count('id'),
        mentors=Count('id', filter=Q(role='mentor')),
        learners=Count('id', filter=Q(role='learner'))
    ).order_by('date')
    
    # Session trends
    session_trends = Booking.objects.filter(
        created_at__gte=start_date
    ).extra({
        'date': 'date(created_at)'
    }).values('date').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        cancelled=Count('id', filter=Q(status='cancelled'))
    ).order_by('date')
    
    # Revenue trends
    revenue_trends = Booking.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).extra({
        'date': 'date(created_at)'
    }).values('date').annotate(
        revenue=Sum('total_amount')
    ).order_by('date')
    
    # Top skills by revenue
    top_skills_revenue = Skill.objects.annotate(
        revenue=Sum(
            'booking_primary_skill__total_amount',
            filter=Q(
                booking_primary_skill__created_at__gte=start_date,
                booking_primary_skill__status='completed'
            )
        )
    ).filter(revenue__gt=0).order_by('-revenue')[:10]
    
    # User activity heatmap
    activity_heatmap = AnalyticsEvent.objects.filter(
        created_at__gte=start_date
    ).extra({
        'hour': 'extract(hour from created_at)',
        'day': 'extract(dow from created_at)'
    }).values('hour', 'day').annotate(
        count=Count('id')
    ).order_by('day', 'hour')
    
    return JsonResponse({
        'user_growth': list(user_growth),
        'session_trends': list(session_trends),
        'revenue_trends': list(revenue_trends),
        'top_skills_revenue': [
            {'name': skill.name, 'revenue': float(skill.revenue or 0)}
            for skill in top_skills_revenue
        ],
        'activity_heatmap': list(activity_heatmap),
        'period': period
    })


@staff_member_required
def admin_user_insights(request):
    """
    Detailed user insights for admins
    """
    # User distribution
    user_distribution = {
        'by_role': User.objects.values('role').annotate(count=Count('id')),
        'by_country': User.objects.exclude(
            country__isnull=True
        ).values('country').annotate(count=Count('id')).order_by('-count')[:10],
        'by_verification': User.objects.values('is_verified').annotate(count=Count('id')),
        'by_activity': {
            'active_30d': User.objects.filter(
                last_active__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'active_7d': User.objects.filter(
                last_active__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'active_24h': User.objects.filter(
                last_active__gte=timezone.now() - timedelta(hours=24)
            ).count(),
        }
    }
    
    # Mentor performance insights
    mentor_insights = User.objects.filter(role='mentor').annotate(
        session_count=Count('mentor_bookings'),
        completed_sessions=Count('mentor_bookings', filter=Q(mentor_bookings__status='completed')),
        total_earnings=Sum('mentor_bookings__total_amount', filter=Q(mentor_bookings__status='completed')),
        avg_rating=Avg('mentor_bookings__learner_rating', filter=Q(mentor_bookings__status='completed'))
    ).filter(session_count__gt=0)
    
    # Learner engagement insights
    learner_insights = User.objects.filter(role='learner').annotate(
        session_count=Count('learner_bookings'),
        completed_sessions=Count('learner_bookings', filter=Q(learner_bookings__status='completed')),
        total_spent=Sum('learner_bookings__total_amount', filter=Q(learner_bookings__status='completed')),
        avg_rating_given=Avg('learner_bookings__learner_rating', filter=Q(learner_bookings__status='completed'))
    ).filter(session_count__gt=0)
    
    context = {
        'user_distribution': user_distribution,
        'mentor_insights': mentor_insights.order_by('-total_earnings')[:20],
        'learner_insights': learner_insights.order_by('-total_spent')[:20],
        'total_mentors': mentor_insights.count(),
        'total_learners': learner_insights.count(),
    }
    
    return render(request, 'admin/user_insights.html', context)


@staff_member_required
def admin_financial_reports(request):
    """
    Financial reports and insights
    """
    period = request.GET.get('period', '30')
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))
    
    # Revenue analytics
    revenue_data = Booking.objects.filter(
        status='completed',
        created_at__gte=start_date
    ).aggregate(
        total_revenue=Sum('total_amount'),
        total_sessions=Count('id'),
        average_session_value=Avg('total_amount')
    )
    
    # Platform commission (assuming 10% commission)
    if revenue_data['total_revenue']:
        revenue_data['platform_commission'] = revenue_data['total_revenue'] * 0.10
        revenue_data['mentor_earnings'] = revenue_data['total_revenue'] * 0.90
    else:
        revenue_data['platform_commission'] = 0
        revenue_data['mentor_earnings'] = 0
    
    # Revenue by skill
    revenue_by_skill = Skill.objects.annotate(
        revenue=Sum(
            'booking_primary_skill__total_amount',
            filter=Q(
                booking_primary_skill__status='completed',
                booking_primary_skill__created_at__gte=start_date
            )
        ),
        sessions=Count(
            'booking_primary_skill',
            filter=Q(
                booking_primary_skill__status='completed',
                booking_primary_skill__created_at__gte=start_date
            )
        )
    ).filter(revenue__gt=0).order_by('-revenue')[:10]
    
    # Top earning mentors
    top_mentors = User.objects.filter(role='mentor').annotate(
        earnings=Sum(
            'mentor_bookings__total_amount',
            filter=Q(
                mentor_bookings__status='completed',
                mentor_bookings__created_at__gte=start_date
            )
        ),
        sessions=Count(
            'mentor_bookings',
            filter=Q(
                mentor_bookings__status='completed',
                mentor_bookings__created_at__gte=start_date
            )
        )
    ).filter(earnings__gt=0).order_by('-earnings')[:10]
    
    context = {
        'revenue_data': revenue_data,
        'revenue_by_skill': revenue_by_skill,
        'top_mentors': top_mentors,
        'period': period,
    }
    
    return render(request, 'admin/financial_reports.html', context)
