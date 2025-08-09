from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import RecurringBookingTemplate


class Command(BaseCommand):
    help = 'Generate bookings from recurring templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='How many days ahead to generate bookings (default: 7)'
        )
        parser.add_argument(
            '--template-id',
            type=int,
            help='Generate bookings for specific template ID only'
        )

    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        template_id = options['template_id']
        
        if template_id:
            templates = RecurringBookingTemplate.objects.filter(
                id=template_id, is_active=True
            )
        else:
            templates = RecurringBookingTemplate.objects.filter(
                is_active=True,
                start_date__lte=timezone.now().date() + timedelta(days=days_ahead)
            )
        
        total_generated = 0
        
        for template in templates:
            try:
                count = template.generate_bookings(days_ahead=days_ahead)
                total_generated += count
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated {count} bookings from template "{template.subject}" (ID: {template.id})'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error generating bookings for template {template.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Total bookings generated: {total_generated}')
        )
