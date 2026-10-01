from django.urls import path
from . import views

urlpatterns = [
    path('buses/', views.bus_list, name='bus_list'),
    path('buses/add/', views.bus_create, name='bus_create'),
    path('buses/<int:pk>/edit/', views.bus_update, name='bus_update'),
    path('buses/<int:pk>/delete/', views.bus_delete, name='bus_delete'),
    
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/add/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/', views.driver_update, name='driver_update'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    
    path('inspectors/', views.inspector_list, name='inspector_list'),
    path('inspectors/add/', views.inspector_create_account, name='inspector_create_account'),
    path('inspectors/<int:pk>/edit/', views.inspector_update, name='inspector_update'),
    path('inspectors/<int:pk>/delete/', views.inspector_delete, name='inspector_delete'),
    
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/add/', views.inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/', views.inspection_report_detail, name='inspection_report_detail'),
    path('inspections/<int:pk>/delete/', views.inspection_delete, name='inspection_delete'),
]
