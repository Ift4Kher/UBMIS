from django.utils import timezone
from .models import Trip
from core.models import SiteSetting

def auto_complete_trips():
    """
    Automates the transition of trips to 'COMPLETED' status based on:
    1. Trips from dates before the current_operating_date.
    2. Trips from today that are well past their departure time (4h buffer).
    This ensures tickets 'vanish' from user dashboards which filter for non-completed trips.
    """
    settings = SiteSetting.objects.first()
    if not settings:
        return
    
    current_operating_date = settings.current_operating_date
    now = timezone.localtime()
    
    # 1. Complete any trips from dates before current_operating_date
    Trip.objects.filter(
        date__lt=current_operating_date,
        status__in=['SCHEDULED', 'RUNNING']
    ).update(status='COMPLETED')
    
    # 2. Complete trips from today that are past departure + 4 hours
    # Fetch today's scheduled/running trips
    today_trips = Trip.objects.filter(
        date=current_operating_date,
        status__in=['SCHEDULED', 'RUNNING']
    )
    
    for trip in today_trips:
        # Get departure time from Trip or Schedule
        dep_time = trip.departure_time or (trip.schedule.departure_time if trip.schedule else None)
        if dep_time:
            # Combine current_operating_date and dep_time into a timezone-aware datetime
            dep_datetime = timezone.make_aware(timezone.datetime.combine(current_operating_date, dep_time))
            
            # If current time is more than 4 hours past departure
            if now > dep_datetime + timezone.timedelta(hours=4):
                trip.status = 'COMPLETED'
                trip.save()
