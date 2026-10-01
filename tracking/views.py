from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from fleet.models import Bus
from .models import BusLocation
import json

@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # In a real app, validate user is a driver and get their assigned bus
            # For simplicity, we expect bus_id in the payload or derive it from user
            bus_id = data.get('bus_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            speed = data.get('speed', 0)
            
            if bus_id and latitude and longitude:
                bus = Bus.objects.get(pk=bus_id)
                BusLocation.objects.create(
                    bus=bus,
                    latitude=latitude,
                    longitude=longitude,
                    speed=speed
                )
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def get_bus_locations(request):
    # Get the latest location for each active bus
    # Logic: Group by bus and take max timestamp
    # Simplified: Just return all recent locations (last 5 mins)
    # Even simpler for prototype: Get last location for all buses
    
    locations = []
    active_buses = Bus.objects.filter(is_active=True)
    for bus in active_buses:
        last_loc = BusLocation.objects.filter(bus=bus).order_by('-timestamp').first()
        if last_loc:
            # Find active trip/route
            from operations.models import Trip
            from django.db.models import Q
            from django.utils import timezone
            today = timezone.now().date()
            
            # Try to find a RUNNING trip first (either via schedule or direct bus assignment)
            active_trip = Trip.objects.filter(
                (Q(schedule__bus=bus) | Q(bus=bus)), 
                status='RUNNING'
            ).first()
            
            if not active_trip:
                # Fallback to SCHEDULED for today
                active_trip = Trip.objects.filter(
                    (Q(schedule__bus=bus) | Q(bus=bus)), 
                    date=today, 
                    status='SCHEDULED'
                ).first()
            
            # Resolve route name
            if active_trip:
                if active_trip.schedule:
                    route_name = active_trip.schedule.route.name
                else:
                    route_name = f"{active_trip.source} to {active_trip.destination}"
            else:
                route_name = "No Active Route"
            
            # Find active driver
            driver_name = active_trip.get_driver_name if active_trip else "Unknown Driver"
            if driver_name == "Driver TBA" and hasattr(bus, 'current_driver'):
                 assignment = bus.current_driver
                 if assignment and assignment.is_active:
                     driver_name = assignment.driver.user.get_full_name() or assignment.driver.user.username

            locations.append({
                'id': bus.id,
                'bus_number': bus.bus_number,
                'type': bus.get_bus_type_display(),
                'lat': last_loc.latitude,
                'lng': last_loc.longitude,
                'speed': last_loc.speed,
                'timestamp': last_loc.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'route_name': route_name,
                'driver_name': driver_name
            })
            
    return JsonResponse({'locations': locations})
    
def map_view(request):
    return render(request, 'tracking/map.html')

def active_buses(request):
    from operations.models import Trip
    # Fetch active trips (Status Running)
    active_trips = Trip.objects.filter(status='RUNNING').select_related('schedule__route', 'schedule__bus', 'bus', 'driver_override')
    
    context = {
        'active_trips': active_trips
    }
    return render(request, 'tracking/active_buses.html', context)
