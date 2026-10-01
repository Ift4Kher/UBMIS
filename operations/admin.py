from django.contrib import admin
from .models import Stop, Route, RouteStop, Schedule, Trip, TripStop

class TripStopInline(admin.TabularInline):
    model = TripStop
    extra = 3

class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1

class RouteAdmin(admin.ModelAdmin):
    inlines = [RouteStopInline]
    list_display = ('name', 'source', 'destination', 'is_active')

class TripAdmin(admin.ModelAdmin):
    inlines = [TripStopInline]
    list_display = ('get_trip_label', 'date', 'status', 'is_special', 'get_driver_name', 'bus')
    list_filter = ('status', 'is_special', 'date')
    search_fields = ('source', 'destination', 'bus__bus_number')

    def get_trip_label(self, obj):
        if obj.schedule:
            return f"{obj.schedule.route.name} ({obj.schedule.departure_time})"
        return f"{obj.source} to {obj.destination}"
    get_trip_label.short_description = 'Trip Description'

admin.site.register(Stop)
admin.site.register(Route, RouteAdmin)
admin.site.register(Schedule)
admin.site.register(Trip, TripAdmin)
