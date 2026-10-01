from django.db import models
from django.conf import settings

class Bus(models.Model):
    BUS_TYPES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
    ]
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bus Name", help_text="e.g. 'Blue Bird', 'Staff Bus 1'")
    bus_number = models.CharField(max_length=20, unique=True, verbose_name="Bus Registration Number")
    bus_type = models.CharField(max_length=10, choices=BUS_TYPES, default='STUDENT')
    capacity = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    fitness_expiry = models.DateField()
    insurance_expiry = models.DateField()
    
    def __str__(self):
        if self.name:
            return f"{self.name} ({self.bus_number})"
        return f"{self.bus_number} ({self.get_bus_type_display()})"

class DriverProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    
    def __str__(self):
        return f"Driver: {self.user.username}"

class BusDriverAssignment(models.Model):
    bus = models.OneToOneField(Bus, on_delete=models.CASCADE, related_name='current_driver')
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class InspectionLog(models.Model):
    STATUS_CHOICES = [('PASS', 'Pass'), ('FAIL', 'Fail')]
    TYPE_CHOICES = [('DAILY', 'Daily'), ('MONTHLY', 'Monthly'), ('EMERGENCY', 'Emergency')]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'INSPECTOR'})
    inspection_date = models.DateTimeField(auto_now_add=True)
    inspection_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    comments = models.TextField(blank=True)
    image_evidence = models.ImageField(upload_to='inspections/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.inspection_type} - {self.status}"

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')]
    PRIORITY_CHOICES = [('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class BusInspection(models.Model):
    RESULT_CHOICES = [('PASS', 'Pass'), ('FAIL', 'Fail')]
    
    # 1. Inspector Information (Auto-filled in view)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'INSPECTOR'})
    inspection_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, help_text="Inspection Location")
    
    # 2. Bus Identification
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='inspections')
    
    # 3. Document Verification
    doc_registration = models.BooleanField(default=True, verbose_name="Registration Certificate")
    doc_route_permit = models.BooleanField(default=True, verbose_name="Route Permit")
    doc_insurance = models.BooleanField(default=True, verbose_name="Insurance")
    doc_fitness = models.BooleanField(default=True, verbose_name="Fitness Certificate (Critical)") # CRITICAL
    doc_tax_token = models.BooleanField(default=True, verbose_name="Tax Token")
    
    # 4. Vehicle Condition
    mech_engine = models.BooleanField(default=True, verbose_name="Engine Condition")
    mech_brake = models.BooleanField(default=True, verbose_name="Brake System (Critical)") # CRITICAL
    mech_steering = models.BooleanField(default=True, verbose_name="Steering System (Critical)") # CRITICAL
    mech_suspension = models.BooleanField(default=True, verbose_name="Suspension")
    mech_electrical = models.BooleanField(default=True, verbose_name="Electrical & Lights")
    
    # 5. Safety Equipment
    safe_fire_extinguisher = models.BooleanField(default=True, verbose_name="Fire Extinguisher (Critical)") # CRITICAL
    safe_first_aid = models.BooleanField(default=True, verbose_name="First Aid Box")
    safe_emergency_exit = models.BooleanField(default=True, verbose_name="Emergency Exit (Critical)") # CRITICAL
    safe_hammer = models.BooleanField(default=True, verbose_name="Emergency Hammer")
    safe_speed_governor = models.BooleanField(default=True, verbose_name="Speed Governor")
    
    # 6. Tyres & Body
    body_tyres = models.BooleanField(default=True, verbose_name="Tyres Condition")
    body_windshield = models.BooleanField(default=True, verbose_name="Windshield & Wipers")
    body_damage = models.BooleanField(default=True, verbose_name="Body Damage")
    
    # 7. Interior & Passenger Safety
    int_seats = models.BooleanField(default=True, verbose_name="Seats Condition")
    int_doors = models.BooleanField(default=True, verbose_name="Doors & Handrails")
    int_overcrowding = models.BooleanField(default=True, verbose_name="Overcrowding Check")
    
    # 8. Emission & Environment
    env_smoke = models.BooleanField(default=True, verbose_name="Smoke Emission")
    env_noise = models.BooleanField(default=True, verbose_name="Noise Level")
    
    # 9. Final Results
    overall_status = models.CharField(max_length=10, choices=RESULT_CHOICES, editable=False)
    allowed_to_operate = models.BooleanField(default=False, editable=False)
    next_inspection_date = models.DateField(null=True, blank=True)
    
    # 10. Remarks & Evidence
    remarks = models.TextField(blank=True)
    photo_evidence = models.ImageField(upload_to='inspection_evidence/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Business Logic: Critical Fields
        critical_fields = [
            self.doc_fitness, self.mech_brake, self.mech_steering, 
            self.safe_fire_extinguisher, self.safe_emergency_exit
        ]
        
        # Check all Boolean fields (they are Pass/Fail)
        all_fields = [
            self.doc_registration, self.doc_route_permit, self.doc_insurance, self.doc_fitness, self.doc_tax_token,
            self.mech_engine, self.mech_brake, self.mech_steering, self.mech_suspension, self.mech_electrical,
            self.safe_fire_extinguisher, self.safe_first_aid, self.safe_emergency_exit, self.safe_hammer, self.safe_speed_governor,
            self.body_tyres, self.body_windshield, self.body_damage,
            self.int_seats, self.int_doors, self.int_overcrowding,
            self.env_smoke, self.env_noise
        ]
        
        # Rule: Any critical fail = Overall FAIL
        if any(not f for f in critical_fields):
            self.overall_status = 'FAIL'
            self.allowed_to_operate = False
        # Rule: Any single fail (even non-critical) = Usually FAIL in strict systems, 
        # but user said "If any critical field fails, overall result = Fail. If all fields pass, overall result = Pass."
        # This implies standard fields might not cause overall Fail? No, usually it does.
        # Let's follow: "If any critical field fails, overall status must automatically be Fail."
        # "If all fields pass, overall result = Pass."
        # What if a non-critical fails? Usually it's still Fail but maybe "Warning"? 
        # User specified: "Overall Status: Pass / Fail"
        elif all(all_fields):
            self.overall_status = 'PASS'
            self.allowed_to_operate = True
        else:
            # If some non-critical failed but all critical passed
            self.overall_status = 'FAIL' # Standards usually require 100% for PASS
            self.allowed_to_operate = False
            
        super().save(*args, **kwargs)
        
        # Business Rule: Failed inspections prevent bus operation
        bus = self.bus
        bus.is_active = self.allowed_to_operate
        bus.save()

    @property
    def score_percentage(self):
        all_checks = [
            self.doc_registration, self.doc_route_permit, self.doc_insurance, self.doc_fitness, self.doc_tax_token,
            self.mech_engine, self.mech_brake, self.mech_steering, self.mech_suspension, self.mech_electrical,
            self.safe_fire_extinguisher, self.safe_first_aid, self.safe_emergency_exit, self.safe_hammer, self.safe_speed_governor,
            self.body_tyres, self.body_windshield, self.body_damage,
            self.int_seats, self.int_doors, self.int_overcrowding,
            self.env_smoke, self.env_noise
        ]
        total = len(all_checks)
        passed = sum(1 for check in all_checks if check)
        return int((passed / total) * 100) if total > 0 else 0

    def get_inspector_name(self):
        if self.inspector:
            return self.inspector.get_full_name() or self.inspector.username
        return "Unknown Inspector"

    def __str__(self):
        return f"Inspection: {self.bus.bus_number} - {self.overall_status} ({self.inspection_date.date()})"
