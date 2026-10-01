from django.db import models
from fleet.models import Bus
from django.conf import settings

class Stop(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    stops = models.ManyToManyField(Stop, through='RouteStop')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    arrival_time_offset = models.PositiveIntegerField(help_text="Minutes from start", default=0)
    
    class Meta:
        ordering = ['order']

class Schedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    departure_time = models.TimeField()
    return_time = models.TimeField(null=True, blank=True, help_text="Time the bus leaves for return trip")
    vehicle_count = models.PositiveIntegerField(default=1, help_text="Number of vehicles assigned")
    route_type = models.CharField(max_length=10, choices=[('REGULAR', 'Regular'), ('SHUTTLE', 'Shuttle')], default='REGULAR')
    days_of_week = models.CharField(max_length=50, help_text="Comma separated days (e.g. Mon,Tue)")
    
    def __str__(self):
        return f"{self.route.name} at {self.departure_time}"

class Trip(models.Model):
    STATUS_CHOICES = [('SCHEDULED', 'Scheduled'), ('RUNNING', 'Running'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    destination = models.CharField(max_length=100, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    is_special = models.BooleanField(default=False, verbose_name="Special Trip (Home Page)")
    driver_override = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip_driver')
    standby_total_slots = models.PositiveIntegerField(default=10, help_text="Number of standby tickets allowed after seats are full")
    @property
    def get_driver_name(self):
        # 1. Check for manual override on the Trip
        if self.driver_override:
            return self.driver_override.get_full_name() or self.driver_override.username
            
        # 2. Check for driver assigned to the Trip's Bus
        try:
            if self.bus and self.bus.current_driver:
                driver = self.bus.current_driver.driver.user
                return driver.get_full_name() or driver.username
        except Exception:
            pass
            
        # 3. Check for driver assigned to the Schedule's Bus
        try:
            if self.schedule and self.schedule.bus and self.schedule.bus.current_driver:
                driver = self.schedule.bus.current_driver.driver.user
                return driver.get_full_name() or driver.username
        except Exception:
            pass
            
        return "Driver TBA"

    def __str__(self):
        if self.schedule:
             return f"Trip: {self.schedule.route.name} on {self.date}"
        return f"Special Trip: {self.source} to {self.destination} on {self.date}"

class TripStop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_stoppages')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    arrival_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.stop.name} for {self.trip}"

class Booking(models.Model):
    BOOKING_TYPES = [('SEAT', 'Seat'), ('STANDBY', 'Standby')]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField(null=True, blank=True)
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPES, default='SEAT')
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='CONFIRMED') # CONFIRMED, CANCELLED
    
    class Meta:
        unique_together = ('trip', 'user')

class CapacityRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Capacity Request: {self.user.username} for {self.trip}"
