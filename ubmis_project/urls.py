from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('fleet/', include('fleet.urls')),
    path('operations/', include('operations.urls')),
    path('tracking/', include('tracking.urls')),
    path('dashboard/', core_views.dashboard_redirect, name='dashboard'),
    path('dashboard/admin/', core_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/inspector/', core_views.inspector_dashboard, name='inspector_dashboard'),
    path('dashboard/driver/', core_views.driver_dashboard, name='driver_dashboard'),
    path('dashboard/student/', core_views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/slider/', core_views.slider_image_list, name='slider_image_list'),
    path('dashboard/admin/slider/add/', core_views.slider_image_add, name='slider_image_add'),
    path('dashboard/admin/slider/<int:pk>/delete/', core_views.slider_image_delete, name='slider_image_delete'),
    path('complaint/submit/', core_views.submit_complaint, name='submit_complaint'),
    path('complaint/my-messages/', core_views.my_complaints, name='my_complaints'),
    path('dashboard/admin/complaints/', core_views.admin_complaint_list, name='admin_complaint_list'),
    path('complaint/<int:pk>/chat/', core_views.complaint_chat, name='complaint_chat'),
    path('dashboard/admin/complaints/<int:pk>/resolve/', core_views.resolve_complaint, name='resolve_complaint'),
    path('dashboard/admin/complaints/<int:pk>/delete/', core_views.admin_complaint_delete, name='admin_complaint_delete'),
    path('dashboard/admin/settings/', core_views.site_settings_view, name='site_settings'),
    path('dashboard/admin/notices/', core_views.admin_notice_list, name='admin_notice_list'),
    path('dashboard/admin/notices/add/', core_views.admin_notice_create, name='admin_notice_create'),
    path('dashboard/admin/notices/<int:pk>/edit/', core_views.admin_notice_update, name='admin_notice_update'),
    path('dashboard/admin/notices/<int:pk>/delete/', core_views.admin_notice_delete, name='admin_notice_delete'),
    path('notice-board/', core_views.notice_list, name='notice_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
