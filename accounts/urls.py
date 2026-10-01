from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
