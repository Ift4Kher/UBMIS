from django.urls import path
from . import views

urlpatterns = [
    path('api/update/', views.update_location, name='update_location'),
    path('api/locations/', views.get_bus_locations, name='get_bus_locations'),
    path('map/', views.map_view, name='map_view'),
    path('active-buses/', views.active_buses, name='active_buses'),
]
