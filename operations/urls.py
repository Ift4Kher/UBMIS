from django.urls import path
from . import views

urlpatterns = [
    path('routes/', views.route_list, name='route_list'),
    path('routes/add/', views.route_create, name='route_create'),
    path('routes/<int:pk>/edit/', views.route_edit, name='route_edit'),
    path('routes/<int:pk>/delete/', views.route_delete, name='route_delete'),
    path('routes/public/', views.public_route_list, name='public_route_list'),
    
    # Stop Management
    path('stops/add/', views.stop_create, name='stop_create'),
    path('stops/<int:pk>/edit/', views.stop_edit, name='stop_edit'),
    path('stops/<int:pk>/delete/', views.stop_delete, name='stop_delete'),
    
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/add/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('schedules/public/', views.public_schedule_list, name='public_schedule_list'),
    
    path('trips/add/', views.trip_create, name='trip_create'),
    path('trips/', views.trip_list, name='trip_list'),
    path('safe-trips/', views.safe_trip_list, name='safe_trip_results'),
    path('trips/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('trips/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    path('trips/<int:pk>/delete/', views.trip_delete, name='trip_delete'),
    path('trips/<int:trip_id>/book/', views.book_seat, name='book_seat'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('trips/<int:trip_id>/request-capacity/', views.request_capacity, name='request_capacity'),
    path('request-capacity/<int:request_id>/resolve/', views.resolve_capacity_request, name='resolve_capacity_request'),
    path('seat-management/', views.seat_management, name='seat_management'),
    path('seat-management/trip/<int:trip_id>/', views.admin_trip_seats, name='admin_trip_seats'),
    path('seat-management/schedule/<int:schedule_id>/', views.admin_schedule_seats, name='admin_schedule_seats'),
    path('trips/<int:trip_id>/toggle-status/', views.toggle_trip_status, name='toggle_trip_status'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('delete-history/', views.delete_booking_history, name='delete_history'),
]
