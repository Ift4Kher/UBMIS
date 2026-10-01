from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import Route, Schedule, Trip, Stop, TripStop, Booking, CapacityRequest
from .forms import RouteForm, ScheduleForm, TripForm, StopForm, RouteStopFormSet, TripStopFormSet

def is_admin(user):
    return user.is_authenticated and user.is_admin()

@login_required
@user_passes_test(is_admin)
def route_list(request):
    routes = Route.objects.all()
    stops = Stop.objects.all()
    return render(request, 'operations/route_list.html', {'routes': routes, 'stops': stops})

@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def route_create(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        formset = RouteStopFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            route = form.save()
            stops = formset.save(commit=False)
            for stop in stops:
                stop.route = route
                stop.save()
            formset.save_m2m()
            messages.success(request, 'Route created successfully.')
            return redirect('route_list')
    else:
        form = RouteForm()
        formset = RouteStopFormSet()
    
    return render(request, 'operations/route_form.html', {'form': form, 'formset': formset, 'title': 'Create Route'})

@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def route_edit(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        formset = RouteStopFormSet(request.POST, instance=route)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save() # Formset handles related object updates automatically with instance
            messages.success(request, 'Route updated successfully.')
            return redirect('route_list')
    else:
        form = RouteForm(instance=route)
        formset = RouteStopFormSet(instance=route)
    
    return render(request, 'operations/route_form.html', {'form': form, 'formset': formset, 'title': 'Edit Route'})

@login_required
@user_passes_test(is_admin)
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully.')
        return redirect('route_list')
    return render(request, 'operations/route_confirm_delete.html', {'route': route})

# Stop Management Views
@login_required
@user_passes_test(is_admin)
def stop_create(request):
    if request.method == 'POST':
        form = StopForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stop created successfully.')
            return redirect('route_list') # Redirect back to the main management page
    else:
        form = StopForm()
    return render(request, 'operations/stop_form.html', {'form': form, 'title': 'Add Stoppage'})

@login_required
@user_passes_test(is_admin)
def stop_edit(request, pk):
    stop = get_object_or_404(Stop, pk=pk)
    if request.method == 'POST':
        form = StopForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stop updated successfully.')
            return redirect('route_list')
    else:
        form = StopForm(instance=stop)
    return render(request, 'operations/stop_form.html', {'form': form, 'title': 'Edit Stoppage'})

@login_required
@user_passes_test(is_admin)
def stop_delete(request, pk):
    stop = get_object_or_404(Stop, pk=pk)
    if request.method == 'POST':
        stop.delete()
        messages.success(request, 'Stop deleted successfully.')
        return redirect('route_list')
    return render(request, 'operations/stop_confirm_delete.html', {'stop': stop})

@login_required
@user_passes_test(is_admin)
def schedule_list(request):
    from core.models import SiteSetting
    settings = SiteSetting.objects.first()

    if request.method == 'POST' and 'update_operating_date' in request.POST:
        operating_date = request.POST.get('operating_date')
        if operating_date:
            from core.models import SiteSetting
            SiteSetting.objects.update_or_create(
                id=settings.id if settings else 1,
                defaults={'current_operating_date': operating_date}
            )
            
            # Immediately refresh trips status based on new date
            from .utils import auto_complete_trips
            auto_complete_trips()
            
            messages.success(request, f"Global operating date updated to {operating_date} and dashboards refreshed.")
        return redirect('schedule_list')

    schedules = Schedule.objects.all()
    return render(request, 'operations/schedule_list.html', {
        'schedules': schedules,
        'site_settings': settings
    })

@login_required
@user_passes_test(is_admin)
def schedule_create(request):
    initial_date = request.GET.get('date')
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            
            # Auto-create Trip if initial_date was provided
            trip_date = request.POST.get('initial_date')
            if trip_date:
                try:
                    Trip.objects.create(
                        schedule=schedule,
                        date=trip_date,
                        status='SCHEDULED'
                    )
                    messages.success(request, f'Schedule and Trip for {trip_date} created successfully.')
                except Exception as e:
                    messages.warning(request, f'Schedule created, but failed to create trip: {e}')
            else:
                messages.success(request, 'Schedule created successfully.')
                
            return redirect('schedule_list')
    else:
        initial_data = {}
        if initial_date:
            import datetime
            try:
                dt = datetime.datetime.strptime(initial_date, '%Y-%m-%d')
                initial_data['days_of_week'] = dt.strftime('%a')
            except ValueError:
                pass
        form = ScheduleForm(initial=initial_data)
        
    return render(request, 'operations/schedule_form.html', {
        'form': form, 
        'title': 'Create Schedule',
        'initial_date': initial_date
    })

@login_required
@user_passes_test(is_admin)
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully.')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'operations/schedule_form.html', {'form': form, 'title': 'Edit Schedule'})

@login_required
@user_passes_test(is_admin)
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully.')
        return redirect('schedule_list')
    return render(request, 'operations/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
@user_passes_test(is_admin)
def trip_create(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        formset = TripStopFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            trip = form.save(commit=False)
            if not trip.schedule:
                trip.is_special = True
            trip.save()
            
            formset.instance = trip
            formset.save()
            
            messages.success(request, 'Trip and Stoppages created successfully.')
            return redirect('trip_list')
    else:
        initial_data = {'is_special': True}
        if request.GET.get('date'):
            initial_data['date'] = request.GET.get('date')
        form = TripForm(initial=initial_data)
        formset = TripStopFormSet()
    
    return render(request, 'operations/trip_form.html', {
        'form': form, 
        'formset': formset,
        'title': 'Create Special Trip'
    })

def trip_detail(request, pk):
    trip = get_object_or_404(
        Trip.objects.select_related(
            'bus', 'driver_override', 'schedule__route'
        ).prefetch_related('trip_stoppages__stop'), 
        pk=pk
    )
    
    # Data Normalization
    if trip.schedule:
        if not trip.source: trip.source = trip.schedule.route.source
        if not trip.destination: trip.destination = trip.schedule.route.destination
        if not trip.departure_time: trip.departure_time = trip.schedule.departure_time
    
    # Extra Info for UI
    route_name = trip.schedule.route.name if trip.schedule else "Special Route"
    bus_obj = trip.bus or (trip.schedule.bus if trip.schedule else None)
    bus_reg_last_4 = bus_obj.bus_number[-4:] if bus_obj and bus_obj.bus_number else None
    
    context = {
        'trip': trip,
        'bus': bus_obj,
        'route_name': route_name,
        'bus_reg_last_4': bus_reg_last_4
    }
    
    return render(request, 'operations/trip_detail.html', context)

@login_required
@user_passes_test(is_admin)
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        formset = TripStopFormSet(request.POST, instance=trip)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Trip updated successfully.')
            return redirect('trip_list')
    else:
        form = TripForm(instance=trip)
        formset = TripStopFormSet(instance=trip)
    
    return render(request, 'operations/trip_form.html', {
        'form': form, 
        'formset': formset,
        'title': 'Edit Trip'
    })

@login_required
@user_passes_test(is_admin)
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Trip deleted successfully.')
        return redirect('trip_list')
    return render(request, 'operations/trip_confirm_delete.html', {'trip': trip})

# Student/Public Views
def trip_list(request):
    from core.models import SiteSetting
    from django.db.models import Q
    from .models import Route, Trip, Schedule, RouteStop, TripStop
    
    site_settings = SiteSetting.objects.first()
    
    print(f"DEBUG: Rendering trip_list. Query: {request.GET.get('q')}")
    today = site_settings.current_operating_date if site_settings else timezone.localdate()
    
    query = request.GET.get('q', '').strip()
    
    # Base collection of results
    matched_trips = []
    
    if query:
        # 1. Search Regular Routes via RouteStops
        # Find routes that contain the requested stop
        routes_query = Route.objects.filter(
            Q(is_active=True) & 
            Q(stops__name__icontains=query)
        ).distinct()
        
        # For these routes, get today's trips
        for route in routes_query:
            schedules = Schedule.objects.filter(route=route)
            for schedule in schedules:
                trip = Trip.objects.filter(schedule=schedule, date=today).first()
                if not trip:
                    trip = Trip.objects.create(
                        schedule=schedule,
                        date=today,
                        status='SCHEDULED',
                        source=route.source,
                        destination=route.destination,
                        departure_time=schedule.departure_time
                    )
                if trip not in matched_trips:
                    matched_trips.append(trip)

        # 2. Search Special Trips via TripStops or Source/Destination
        special_query = Trip.objects.filter(
            Q(is_special=True) & Q(date__gte=today) & (
                Q(source__icontains=query) | 
                Q(destination__icontains=query) |
                Q(trip_stoppages__stop__name__icontains=query)
            )
        ).distinct()
        
        for trip in special_query:
            if trip not in matched_trips:
                matched_trips.append(trip)
    else:
        # If no search, show special trips as before
        # If no search, show:
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'ADMIN'):
            # Admin gets ALL special trips (past, future, cancelled), ordered by date
            matched_trips = list(Trip.objects.filter(is_special=True).order_by('date'))
        else:
            matched_trips = list(Trip.objects.filter(status__in=['SCHEDULED', 'RUNNING'], is_special=True).order_by('date'))

    # Sort results by time
    matched_trips.sort(key=lambda x: x.departure_time or (x.schedule.departure_time if x.schedule else timezone.datetime.min.time()))

    # Formatter-proofing: Pre-calculate display strings in Python
    for t in matched_trips:
        t.display_source = t.source if t.source else (t.schedule.route.source if t.schedule else "Unknown")
        t.display_destination = t.destination if t.destination else (t.schedule.route.destination if t.schedule else "Unknown")
        d_time = t.departure_time if t.departure_time else (t.schedule.departure_time if t.schedule else None)
        t.display_time = d_time.strftime("%I:%M %p") if d_time else "TBA"
        t.display_date = t.date.strftime("%b %d") if t.date else ""
        t.type_label = "SPECIAL" if t.is_special else "REGULAR"

        # Fetch and format stoppages
        if t.is_special:
            # Special trips use TripStop
            stops = t.trip_stoppages.all().order_by('order').select_related('stop')
            t.display_stops = " → ".join([s.stop.name for s in stops]) if stops else ""
        elif t.schedule and t.schedule.route:
            # Regular trips use RouteStop via the schedule's route
            stops = RouteStop.objects.filter(route=t.schedule.route).order_by('order').select_related('stop')
            t.display_stops = " → ".join([s.stop.name for s in stops]) if stops else ""
        else:
            t.display_stops = ""

    return render(request, 'operations/trip_list.html', {
        'trips': matched_trips,
        'search_query': query,
        'is_search': bool(query),
        'activation_time': timezone.make_aware(datetime.combine(timezone.localtime().date(), site_settings.booking_activation_datetime)) if site_settings and site_settings.booking_activation_datetime else None,
        'shuttle_activation_time': timezone.make_aware(datetime.combine(timezone.localtime().date(), site_settings.shuttle_booking_start_time)) if site_settings and site_settings.shuttle_booking_start_time else None,
        'now': timezone.now()
    })

def safe_trip_list(request):
    from core.models import SiteSetting
    from django.db.models import Q
    from .models import Route, Trip, Schedule, RouteStop, TripStop
    
    site_settings = SiteSetting.objects.first()
    today = site_settings.current_operating_date if site_settings else timezone.localdate()
    query = request.GET.get('q', '').strip()
    matched_trips = []
    
    if query:
        # Re-use search logic but render DIFFERENT template
        routes_query = Route.objects.filter(Q(is_active=True) & Q(stops__name__icontains=query)).distinct()
        for route in routes_query:
            schedules = Schedule.objects.filter(route=route)
            for schedule in schedules:
                trip = Trip.objects.filter(schedule=schedule, date=today).first()
                if trip and trip not in matched_trips: matched_trips.append(trip)
    
    return render(request, 'operations/safe_results.html', {
        'trips': matched_trips,
        'search_query': query,
        'is_search': bool(query)
    })

@login_required
def book_seat(request, trip_id):
    # Restriction: Only Students and Faculty can book
    if not (request.user.is_student() or request.user.is_faculty()):
        messages.error(request, "Only students and faculty are authorized to book seats.")
        return redirect('dashboard')

    from core.models import SiteSetting
    site_settings = SiteSetting.objects.first()
    today = site_settings.current_operating_date if site_settings else timezone.localdate()
    
    # Get or create Trip
    try:
        trip = Trip.objects.get(pk=trip_id)
    except Trip.DoesNotExist:
        schedule = get_object_or_404(Schedule, pk=trip_id)
        trip = Trip.objects.filter(schedule=schedule, date=today).first()
        if not trip:
            trip = Trip.objects.create(schedule=schedule, date=today, status='SCHEDULED')

    # Data Normalization for Header
    if trip.schedule:
        if not trip.source: trip.source = trip.schedule.route.source
        if not trip.destination: trip.destination = trip.schedule.route.destination
        if not trip.departure_time: trip.departure_time = trip.schedule.departure_time

    bus = trip.bus or (trip.schedule.bus if trip.schedule else None)
    capacity = bus.capacity if bus else 40
    
    # Determine if this is a Shuttle Trip
    is_shuttle = trip.is_special or (trip.schedule and trip.schedule.route_type == 'SHUTTLE')

    # Date Validation
    if site_settings and trip.date < site_settings.current_operating_date:
        messages.error(request, f"This trip is from a past date ({trip.date}) and cannot be booked.")
        return redirect('dashboard')


    # Check global booking window
    if site_settings:
        current_time = timezone.localtime().time()
        
        # 1. Activation Timer Check
        if not trip.is_special:
            if is_shuttle:
                # Check Shuttle Timer
                if site_settings.shuttle_booking_activation_datetime:
                    if current_time < site_settings.shuttle_booking_activation_datetime:
                         messages.error(request, f"Shuttle booking opens daily at {site_settings.shuttle_booking_activation_datetime.strftime('%I:%M %p')}.")
                         return redirect('dashboard')
            else:
                # Check Regular Timer
                if site_settings.booking_activation_datetime:
                    if current_time < site_settings.booking_activation_datetime:
                        messages.error(request, f"Regular booking opens daily at {site_settings.booking_activation_datetime.strftime('%I:%M %p')}.")
                        return redirect('dashboard')

        # 2. Daily Window Check
        if not trip.is_special:
            if is_shuttle:
                # Check Shuttle Window
                if not (site_settings.shuttle_booking_start_time <= current_time <= site_settings.shuttle_booking_end_time):
                    messages.error(request, f"Shuttle booking is only allowed between {site_settings.shuttle_booking_start_time.strftime('%I:%M %p')} and {site_settings.shuttle_booking_end_time.strftime('%I:%M %p')}.")
                    return redirect('dashboard')
            else:
                # Check Regular Window
                if not (site_settings.booking_start_time <= current_time <= site_settings.booking_end_time):
                    messages.error(request, f"Regular bus booking is only allowed between {site_settings.booking_start_time.strftime('%I:%M %p')} and {site_settings.booking_end_time.strftime('%I:%M %p')}.")
                    return redirect('dashboard')
    
    # Check for ANY booking for THIS trip (including cancelled ones)
    user_booking_this_trip = Booking.objects.filter(user=request.user, trip=trip).first()
    
    # Check for CONFIRMED bookings on OTHER trips today
    other_booking_today = Booking.objects.filter(
        user=request.user, 
        trip__date=trip.date, 
        status='CONFIRMED'
    ).exclude(trip=trip).first()

    if request.method == 'POST':
        # Restriction 1: Daily Limit (Cannot book THIS trip if you have a CONFIRMED one elsewhere)
        if other_booking_today:
            messages.warning(request, f"You already have a confirmed booking for {trip.date} on another trip. Please cancel it first.")
            return redirect('dashboard')
        
        # Restriction 2: Duplication (Cannot book THIS trip if you ALREADY have a CONFIRMED one here)
        if user_booking_this_trip and user_booking_this_trip.status == 'CONFIRMED':
            messages.info(request, "You already have a confirmed booking for this trip.")
            return redirect('dashboard')
            
        action = request.POST.get('action')
        if action == 'book_seat':
            seat_number = request.POST.get('seat_number')
            if not seat_number:
                messages.error(request, "Please select a seat.")
                return redirect('book_seat', trip_id=trip_id)
            
            seat_number = int(seat_number)
            if Booking.objects.filter(trip=trip, seat_number=seat_number, status='CONFIRMED').exists():
                messages.error(request, "This seat is already booked.")
                return redirect('book_seat', trip_id=trip_id)
            
            # Use update_or_create to avoid IntegrityError if a cancelled/old record exists
            Booking.objects.update_or_create(
                trip=trip, 
                user=request.user,
                defaults={
                    'seat_number': seat_number,
                    'booking_type': 'SEAT',
                    'status': 'CONFIRMED'
                }
            )
            messages.success(request, f"Seat {seat_number} booked successfully!")
            return redirect('dashboard')
            
        elif action == 'book_standby':
            booked_count = Booking.objects.filter(trip=trip, booking_type='SEAT', status='CONFIRMED').count()
            if booked_count < capacity:
                messages.error(request, "Seats are still available. Please select a seat.")
                return redirect('book_seat', trip_id=trip_id)
                
            Booking.objects.update_or_create(
                trip=trip, 
                user=request.user,
                defaults={
                    'booking_type': 'STANDBY',
                    'status': 'CONFIRMED',
                    'seat_number': None
                }
            )
            messages.success(request, "Standby ticket booked successfully!")
            return redirect('dashboard')

    # For UI: Only show success/limit states if booking is CONFIRMED
    confirmed_booking_this_trip = user_booking_this_trip if user_booking_this_trip and user_booking_this_trip.status == 'CONFIRMED' else None

    context = {
        'trip': trip,
        'capacity': capacity,
        'booked_seats': list(Booking.objects.filter(trip=trip, status='CONFIRMED', booking_type='SEAT').values_list('seat_number', flat=True)),
        'user_booking': confirmed_booking_this_trip,
        'other_booking': other_booking_today,
        'range_capacity': range(1, capacity + 1)
    }
    return render(request, 'operations/seat_selection.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.seat_number = None  # Release the seat
        booking.save()
        messages.success(request, "Your booking has been cancelled successfully.")
    return redirect('dashboard')

@login_required
def request_capacity(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    # Check if a request already exists for this user and trip
    if not CapacityRequest.objects.filter(user=request.user, trip=trip, is_resolved=False).exists():
        CapacityRequest.objects.create(user=request.user, trip=trip)
        messages.success(request, "Capacity request sent to admin. Thank you for your feedback.")
    else:
        messages.info(request, "You have already sent a capacity request for this trip.")
    return redirect('trip_list')

@login_required
@user_passes_test(is_admin)
def seat_management(request):
    from core.models import SiteSetting
    from django.db.models import Count
    
    today = timezone.localdate()
    settings = SiteSetting.objects.first()
    
    # Handle Global Booking Time Updates
    if request.method == 'POST' and 'update_booking_times' in request.POST:
        start_time = request.POST.get('booking_start_time')
        end_time = request.POST.get('booking_end_time')
        # Shuttle Window
        shuttle_start = request.POST.get('shuttle_booking_start_time')
        shuttle_end = request.POST.get('shuttle_booking_end_time')
        
        activation_time = request.POST.get('booking_activation_datetime')
        shuttle_activation_time = request.POST.get('shuttle_booking_activation_datetime')
        
        if settings:
            settings.booking_start_time = start_time
            settings.booking_end_time = end_time
            
            settings.shuttle_booking_start_time = shuttle_start if shuttle_start else '00:00:00'
            settings.shuttle_booking_end_time = shuttle_end if shuttle_end else '23:59:59'
            
            settings.booking_activation_datetime = activation_time if activation_time else None
            settings.shuttle_booking_activation_datetime = shuttle_activation_time if shuttle_activation_time else None
            settings.save()
            
            # Refresh trips status when booking window changes
            from .utils import auto_complete_trips
            auto_complete_trips()
            
            messages.success(request, "Global booking settings updated and dashboards refreshed.")
        return redirect('seat_management')

    # Get all regular schedules
    schedules = Schedule.objects.all().select_related('route', 'bus').order_by('departure_time')
    
    # Enrich schedules with today's trip data if it exists
    current_time = timezone.localtime().time()
    booking_is_active = False
    if settings:
        booking_is_active = settings.booking_start_time <= current_time <= settings.booking_end_time

    for schedule in schedules:
        trip = Trip.objects.filter(schedule=schedule, date=today).first()
        if trip:
            schedule.today_trip = trip
            schedule.seat_count = Booking.objects.filter(trip=trip, booking_type='SEAT', status='CONFIRMED').count()
            schedule.standby_count = Booking.objects.filter(trip=trip, booking_type='STANDBY', status='CONFIRMED').count()
            bus = trip.bus or schedule.bus
            schedule.total_capacity = bus.capacity if bus else 40
            schedule.remaining = (schedule.total_capacity + trip.standby_total_slots) - (schedule.seat_count + schedule.standby_count)
            schedule.occupancy_pct = (schedule.seat_count * 100 // schedule.total_capacity) if schedule.total_capacity > 0 else 0
            schedule.bookings_list = Booking.objects.filter(trip=trip).select_related('user').order_by('booking_type', 'seat_number')
        else:
            schedule.today_trip = None
            schedule.occupancy_pct = 0
            schedule.seat_count = 0

    context = {
        'schedules': schedules,
        'site_settings': settings,
        'booking_is_active': booking_is_active,
    }
    return render(request, 'operations/seat_management.html', context)

@login_required
@user_passes_test(is_admin)
def resolve_capacity_request(request, request_id):
    req = get_object_or_404(CapacityRequest, pk=request_id)
    req.is_resolved = True
    req.save()
    messages.success(request, "Capacity request marked as resolved.")
    return redirect('admin_dashboard')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'operations/my_bookings.html', {'bookings': bookings})

@login_required
def delete_booking_history(request):
    if request.method == 'POST':
        # Deleting all bookings for the current user
        Booking.objects.filter(user=request.user).delete()
        messages.success(request, "Your booking history has been cleared.")
    return redirect('my_bookings')

# Public Schedule List View
def public_schedule_list(request):
    from core.models import SiteSetting
    from django.utils import timezone
    
    settings = SiteSetting.objects.first()
    today = settings.current_operating_date if settings else timezone.localdate()
    current_time = timezone.localtime().time()
    
    booking_is_active = True
    shuttle_booking_is_active = True
    if settings:
        booking_is_active = settings.booking_start_time <= current_time <= settings.booking_end_time
        shuttle_booking_is_active = settings.shuttle_booking_start_time <= current_time <= settings.shuttle_booking_end_time
        
    schedules = Schedule.objects.select_related('route', 'bus').order_by('departure_time')
    
    # Enrich with today's trip
    current_weekday = today.strftime('%a').lower() # mon, tue, etc.
    
    for s in schedules:
        # Check if this schedule runs today
        runs_today = False
        if s.days_of_week:
            # Normalize DB values: lowercase, strip text
            days_list = [d.strip().lower() for d in s.days_of_week.split(',')]
            
            # Handle standard names (mon, tue) and numeric (0=mon, 6=sun)
            # Python weekday: Mon=0, Sun=6. 
            # Let's map current_weekday to potential matches
            
            # Map for safety if DB uses full names or different abbr
            # We compare against 'mon', 'tue', etc.
            
            if current_weekday in days_list:
                runs_today = True
            
            # Additional check for numeric strings if used
            # today.weekday() returns 0 for Mon, 6 for Sun
            current_weekday_num = str(today.weekday()) 
            if current_weekday_num in days_list:
                runs_today = True
        else:
            # Fallback: if no specific days set, assume daily
            runs_today = True 

        s.next_trip = Trip.objects.filter(schedule=s, date=today, status__in=['SCHEDULED', 'RUNNING']).first()
         
        if not s.next_trip and runs_today:
            # Auto-create the trip so it appears available
            try:
                s.next_trip = Trip.objects.create(
                    schedule=s,
                    date=today,
                    status='SCHEDULED',
                    source=s.route.source,
                    destination=s.route.destination,
                    departure_time=s.departure_time
                )
            except Exception:
                # Potential race condition or error, just ignore
                pass
        
    context = {
        'schedules': schedules,
        'booking_is_active': booking_is_active,
        'shuttle_booking_is_active': shuttle_booking_is_active,
        'activation_time': timezone.make_aware(datetime.combine(timezone.localtime().date(), settings.booking_activation_datetime)) if settings and settings.booking_activation_datetime else None,
        'shuttle_activation_time': timezone.make_aware(datetime.combine(timezone.localtime().date(), settings.shuttle_booking_start_time)) if settings and settings.shuttle_booking_start_time else None,
        'now': timezone.now()
    }
    return render(request, 'operations/public_schedule_list.html', context)

# Public Route List View
def public_route_list(request):
    routes = Route.objects.filter(is_active=True).prefetch_related('routestop_set__stop').order_by('name')
    return render(request, 'operations/public_route_list.html', {'routes': routes})
@login_required
def toggle_trip_status(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    # Security: In a real app, ensure this bus belongs to the driver
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Trip.STATUS_CHOICES):
            trip.status = new_status
            trip.save()
            return JsonResponse({'status': 'success', 'new_status': trip.get_status_display()})
    return JsonResponse({'status': 'error'}, status=400)
@login_required
@user_passes_test(is_admin)
def admin_trip_seats(request, trip_id):
    trip = get_object_or_404(Trip.objects.select_related('bus', 'schedule__route'), pk=trip_id)
    bus = trip.bus or (trip.schedule.bus if trip.schedule else None)
    capacity = bus.capacity if bus else 40
    
    bookings = Booking.objects.filter(trip=trip, status='CONFIRMED').select_related('user')
    booked_seats_map = {b.seat_number: b for b in bookings if b.booking_type == 'SEAT'}
    
    seats = []
    for s in range(1, capacity + 1):
        seats.append({
            'number': s,
            'booking': booked_seats_map.get(s)
        })
        
    standby_bookings = [b for b in bookings if b.booking_type == 'STANDBY']
    
    context = {
        'trip': trip,
        'capacity': capacity,
        'seats': seats,
        'standby_bookings': standby_bookings,
    }
    return render(request, 'operations/admin_trip_seats.html', context)


@login_required
@user_passes_test(is_admin)
def admin_schedule_seats(request, schedule_id):
    today = timezone.localdate()
    schedule = get_object_or_404(Schedule.objects.select_related('bus', 'route'), pk=schedule_id)
    
    # Get or create today's trip for this schedule
    trip = Trip.objects.filter(schedule=schedule, date=today).first()
    if not trip:
        trip = Trip.objects.create(
            schedule=schedule,
            date=today,
            status='SCHEDULED',
            source=schedule.route.source,
            destination=schedule.route.destination,
            departure_time=schedule.departure_time
        )
        messages.info(request, f"New trip record generated for {schedule.route.name} today.")
        
    return admin_trip_seats(request, trip.id)
