from django.contrib import admin
from .models import Bus, DriverProfile, BusInspection

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'bus_type', 'capacity', 'is_active')
    list_filter = ('bus_type', 'is_active')
    search_fields = ('bus_number', 'name')

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number')
    search_fields = ('user__username', 'license_number')

@admin.register(BusInspection)
class BusInspectionAdmin(admin.ModelAdmin):
    list_display = ('bus', 'inspector', 'inspection_date', 'overall_status', 'allowed_to_operate')
    list_filter = ('overall_status', 'allowed_to_operate', 'inspection_date')
    search_fields = ('bus__bus_number', 'inspector__username', 'location')
    readonly_fields = ('inspection_date', 'overall_status', 'allowed_to_operate')
