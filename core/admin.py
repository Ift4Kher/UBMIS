from django.contrib import admin
from .models import SliderImage, Notice

# Register your models here.
@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
