from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import SliderImage, SiteSetting, Notice, Complaint, ComplaintMessage
from .forms import NoticeForm, SliderImageForm, SiteSettingForm, ComplaintForm
from operations.models import Trip, Route, Schedule, Booking, CapacityRequest
from fleet.models import Bus, DriverProfile, MaintenanceRequest, BusInspection
from operations.utils import auto_complete_trips

def home(request):
    
    # Run auto-completion check to ensure past tickets vanish
    auto_complete_trips()
    
    site_settings = SiteSetting.objects.first()
    today = site_settings.current_operating_date if site_settings else timezone.now().date()
    
    # Regular scheduled trips for the selected day
    trips = Trip.objects.filter(
        status__in=['SCHEDULED', 'RUNNING'], 
        is_special=False,
        date=today
    ).order_by('schedule__departure_time')[:6]
    
    # Special Trips (Show upcoming ones starting from today)
    special_trips = Trip.objects.filter(
        status__in=['SCHEDULED', 'RUNNING'], 
        is_special=True, 
        date__gte=today
    ).select_related(
        'driver_override', 
        'bus__current_driver__driver__user'
    ).prefetch_related('trip_stoppages__stop').order_by('date', 'departure_time')
    
    slider_images = SliderImage.objects.filter(is_active=True).order_by('-created_at')
    
    # Fetch active routes with stops for the Routes & Stoppages section
    routes_queryset = Route.objects.filter(is_active=True).prefetch_related('routestop_set__stop').order_by('name')
    routes_count = routes_queryset.count()
    routes = routes_queryset[:4]
    
    # Fetch Schedules for the Transport Schedule Table
    schedules_queryset = Schedule.objects.select_related('route', 'bus').order_by('departure_time')
    schedules_count = schedules_queryset.count()
    schedules = list(schedules_queryset[:5])
    
    # Enrich with today's trip
    current_weekday = today.strftime('%a').lower()

    for s in schedules:
        # Check if schedule runs today
        runs_today = False
        if s.days_of_week:
            days_list = [d.strip().lower() for d in s.days_of_week.split(',')]
            if current_weekday in days_list:
                runs_today = True
            current_weekday_num = str(today.weekday())
            if current_weekday_num in days_list:
                runs_today = True
        else:
            runs_today = True

        s.next_trip = Trip.objects.filter(schedule=s, date=today, status__in=['SCHEDULED', 'RUNNING']).first()
        
        if not s.next_trip and runs_today:
            # Auto-create trip so we pass a valid Trip ID, avoiding Schedule ID collision
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
                pass
    
    # Global Booking Check
    settings = SiteSetting.objects.first()
    booking_is_active = True
    shuttle_booking_is_active = True
    if settings:
        current_time = timezone.localtime().time()
        booking_is_active = settings.booking_start_time <= current_time <= settings.booking_end_time
        shuttle_booking_is_active = settings.shuttle_booking_start_time <= current_time <= settings.shuttle_booking_end_time
    
    # Notification Logic
    last_check = request.session.get('last_notice_check')
    notices_query = Notice.objects.filter(is_active=True)
    
    if last_check:
        try:
            last_check_dt = timezone.datetime.fromisoformat(last_check)
            new_notices_count = notices_query.filter(updated_at__gt=last_check_dt).count()
        except ValueError:
            new_notices_count = notices_query.count()
    else:
        new_notices_count = notices_query.count()

    context = {
        'trips': trips, 
        'special_trips': special_trips,
        'slider_images': slider_images, 
        'routes': routes,
        'routes_count': routes_count,
        'schedules': schedules,
        'schedules_count': schedules_count,
        'booking_is_active': booking_is_active,
        'shuttle_booking_is_active': shuttle_booking_is_active,
        'today': today,
        'new_notices_count': new_notices_count,
    }
    return render(request, 'core/home.html', context)

@login_required
def notice_list(request):
    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    
    # Update last check timestamp
    request.session['last_notice_check'] = timezone.now().isoformat()
    
    return render(request, 'core/notice_list.html', {'notices': notices})

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin():
        return redirect('admin_dashboard')
    elif user.is_inspector():
        return redirect('inspector_dashboard')
    elif user.is_driver():
        return redirect('driver_dashboard')
    elif user.is_student() or user.is_faculty():
        return redirect('student_dashboard')
    else:
        return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return redirect('dashboard')
        
    today = timezone.localdate()
    
    # Summary logic
    trips_with_bookings = Trip.objects.filter(status='RUNNING').annotate(booking_count=Count('booking'))
    capacity_requests = CapacityRequest.objects.filter(is_resolved=False).select_related('user', 'trip')
    
    recent_inspections = BusInspection.objects.select_related('bus', 'inspector').order_by('-inspection_date')[:5]

    context = {
        'total_buses': Bus.objects.count(),
        'active_trips': Trip.objects.filter(status='RUNNING').count(),
        'maintenance_alerts': MaintenanceRequest.objects.filter(status='PENDING').count(),
        'total_drivers': DriverProfile.objects.count(),
        'total_routes': Route.objects.count(),
        'trip_bookings': trips_with_bookings,
        'capacity_requests': capacity_requests,
        'recent_inspections': recent_inspections,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def inspector_dashboard(request):
    return render(request, 'core/inspector_dashboard.html')

@login_required
def driver_dashboard(request):
    try:
        driver_profile = request.user.driver_profile
        # Get all buses assigned to this driver
        assignments = driver_profile.busdriverassignment_set.filter(is_active=True).select_related('bus')
        assigned_buses = [a.bus for a in assignments]
        assigned_bus = assigned_buses[0] if assigned_buses else None
        
        site_settings = SiteSetting.objects.first()
        today = site_settings.current_operating_date if site_settings else timezone.localdate()
        
        # Fetch all assigned trips for today (Regular Trips)
        assigned_trips_query = Q(driver_override=request.user)
        if assigned_buses:
            assigned_trips_query |= Q(schedule__bus__in=assigned_buses) | Q(bus__in=assigned_buses)
            
        all_assigned_trips = Trip.objects.filter(
            assigned_trips_query,
            date=today,
            status__in=['SCHEDULED', 'RUNNING']
        ).distinct().order_by('departure_time', 'schedule__departure_time')

        # Current Trip (next one chronologically today)
        current_trip = all_assigned_trips.first()
        
        # Special Trips (Show all upcoming special trips assigned to this driver)
        special_trips = Trip.objects.filter(
            assigned_trips_query,
            is_special=True,
            date__gte=today,
            status__in=['SCHEDULED', 'RUNNING']
        ).distinct().order_by('date', 'departure_time')
        
        assigned_routes = []
        if assigned_buses:
            assigned_routes = set()
            for bus in assigned_buses:
                assigned_routes.update(s.route for s in bus.schedule_set.select_related('route').all())

        # Additional Data for "Vehicle Status"
        inspections = []
        booking_count = 0
        if assigned_bus:
            inspections = BusInspection.objects.filter(bus=assigned_bus).order_by('-inspection_date')[:5]
            
        if current_trip:
            booking_count = Booking.objects.filter(trip=current_trip, status='CONFIRMED').count()
        
        # All extra REGULAR trips today (excluding the current/main one if it's regular)
        other_trips = all_assigned_trips.filter(is_special=False)
        if current_trip and not current_trip.is_special:
            other_trips = other_trips.exclude(pk=current_trip.pk)
        
    except Exception:
        driver_profile = None
        assigned_bus = None
        current_trip = None
        special_trips = []
        other_trips = []
        assigned_routes = []
        inspections = []
        booking_count = 0

    tab = request.GET.get('tab', 'overview')
    context = {
        'driver_profile': driver_profile,
        'assigned_bus': assigned_bus,
        'current_trip': current_trip,
        'special_trips': special_trips,
        'other_trips': other_trips,
        'assigned_routes': assigned_routes,
        'inspections': inspections,
        'booking_count': booking_count,
        'active_tab': tab,
        # Simplified variables to prevent template tag splitting
        'bus_type': assigned_bus.get_bus_type_display() if assigned_bus else '',
        'bus_cap': assigned_bus.capacity if assigned_bus else '',
        'trip_status': current_trip.get_status_display() if current_trip else '',
        'trip_source': current_trip.source if current_trip else '',
        'trip_dest': current_trip.destination if current_trip else '',
        'role_display': request.user.get_role_display(),
    }
    return render(request, 'core/driver_dashboard.html', context)

@login_required
def student_dashboard(request):
    
    # Refresh trips status for student dashboard
    auto_complete_trips()
    
    # Get today's date from settings
    site_settings = SiteSetting.objects.first()
    today = site_settings.current_operating_date if site_settings else timezone.now().date()

    active_bookings = Booking.objects.filter(
        user=request.user, 
        status='CONFIRMED',
    ).filter(
        Q(trip__status__in=['SCHEDULED', 'RUNNING']) | 
        Q(trip__status='COMPLETED', trip__date=today)
    ).select_related('trip__schedule__route', 'trip__bus')
    
    return render(request, 'core/student_dashboard.html', {
        'active_bookings': active_bookings
    })
@login_required
def slider_image_list(request):
    # Deprecated: Redirects to site settings which now contains this list
    return redirect('site_settings')

@login_required
def slider_image_add(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SliderImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('site_settings')
    else:
        form = SliderImageForm()
    return render(request, 'core/slider_image_form.html', {'form': form, 'title': 'Add Slider Image'})

@login_required
def slider_image_delete(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    image = get_object_or_404(SliderImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        return redirect('site_settings')
    return render(request, 'core/slider_image_confirm_delete.html', {'image': image})

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Your complaint has been submitted. You can chat with the admin here.')
            return redirect('complaint_chat', pk=complaint.pk)
    else:
        form = ComplaintForm()
    return render(request, 'core/complaint_form.html', {'form': form})

@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'core/my_complaints.html', {'complaints': complaints})

@login_required
def admin_complaint_list(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    complaints = Complaint.objects.all().order_by('-updated_at') # Order by latest activity
    return render(request, 'core/admin_complaint_list.html', {'complaints': complaints})

@login_required
def complaint_chat(request, pk):
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Security: Only Admin or the User who created it can view
    if not request.user.is_admin() and complaint.user != request.user:
        return redirect('dashboard')
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ComplaintMessage.objects.create(
                complaint=complaint,
                sender=request.user,
                message=message_text
            )
            complaint.updated_at = timezone.now()
            complaint.status = 'PENDING' # Re-open if new message
            complaint.save()
            return redirect('complaint_chat', pk=pk)

    messages = complaint.messages.all().order_by('created_at')
    return render(request, 'core/complaint_chat.html', {'complaint': complaint, 'chat_messages': messages})

@login_required
def resolve_complaint(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        complaint.status = 'RESOLVED'
        complaint.save()
        messages.success(request, 'Complaint marked as resolved.')
    return redirect('admin_complaint_list')

@login_required
def admin_complaint_delete(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted successfully.')
        return redirect('admin_complaint_list')
    return render(request, 'core/admin_complaint_confirm_delete.html', {'complaint': complaint})

@login_required
def site_settings_view(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    
    # Get the first setting object or None
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        # If setting exists, update it. If not, create new (instance=None)
        form = SiteSettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            # Check if operating date has changed
            if 'current_operating_date' in form.changed_data:
                new_date = form.cleaned_data['current_operating_date']
                
                # Bulk update Trip dates and reset status
                from operations.models import Trip
                # Only update Scheduled, Running, or Completed trips (preserve Cancelled history if needed, or update all?)
                # Requirement: "every bus schedule date will be update that date"
                # Simulation Reset: Move all relevant trips to new date and reset status to SCHEDULED
                Trip.objects.filter(
                    status__in=['SCHEDULED', 'RUNNING', 'COMPLETED']
                ).update(date=new_date, status='SCHEDULED')
                
                messages.warning(request, f"Global operating date updated to {new_date}. All trips moved and reset to SCHEDULED.")

            form.save()
            messages.success(request, 'Site settings updated successfully.')
            return redirect('site_settings')
    else:
        form = SiteSettingForm(instance=setting)
    
    return render(request, 'core/site_settings.html', {
        'form': form,
        'slider_images': SliderImage.objects.all().order_by('-created_at')
    })
@login_required
def admin_notice_list(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'core/admin_notice_list.html', {'notices': notices})

@login_required
def admin_notice_create(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice created successfully.')
            return redirect('admin_notice_list')
    else:
        form = NoticeForm()
    return render(request, 'core/admin_notice_form.html', {'form': form, 'title': 'Add Notice'})

@login_required
def admin_notice_update(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice updated successfully.')
            return redirect('admin_notice_list')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'core/admin_notice_form.html', {'form': form, 'title': 'Edit Notice'})

@login_required
def admin_notice_delete(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, 'Notice deleted successfully.')
        return redirect('admin_notice_list')
    return render(request, 'core/admin_notice_confirm_delete.html', {'notice': notice})
