from django import forms
from .models import SliderImage, Complaint, SiteSetting

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['auth_image', 'site_logo', 'homepage_video', 
                  'booking_start_time', 'booking_end_time', 
                  'shuttle_booking_start_time', 'shuttle_booking_end_time',
                  'booking_activation_datetime', 'shuttle_booking_activation_datetime',
                  'current_operating_date']
        widgets = {
            'auth_image': forms.FileInput(attrs={'class': 'form-control'}),
            'site_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'homepage_video': forms.FileInput(attrs={'class': 'form-control'}),
            'booking_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'booking_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shuttle_booking_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shuttle_booking_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'booking_activation_datetime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shuttle_booking_activation_datetime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'current_operating_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class SliderImageForm(forms.ModelForm):
    class Meta:
        model = SliderImage
        fields = ['image', 'caption', 'is_active']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'image': 'Recommended Size: 1920x650 pixels (Landscape ratio 3:1).',
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief subject of your complaint'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your issue in detail...'}),
        }

from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notice Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Notice Content'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
