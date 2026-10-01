from django import forms
from django.forms import inlineformset_factory
from .models import Route, Stop, Schedule, Trip, RouteStop, TripStop

class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Main Gate'}),
        }

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'source', 'destination', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RouteStopForm(forms.ModelForm):
    stop_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stop Name'}))
    
    class Meta:
        model = RouteStop
        fields = ['order', 'arrival_time_offset'] # stop is handled manually
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Seq'}),
            'arrival_time_offset': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['stop_name'].initial = self.instance.stop.name

    def save(self, commit=True):
        instance = super().save(commit=False)
        stop_name = self.cleaned_data.get('stop_name')
        if stop_name:
            stop, created = Stop.objects.get_or_create(name=stop_name)
            instance.stop = stop
        if commit:
            instance.save()
        return instance

# Inline formset to manage stops for a route
RouteStopFormSet = inlineformset_factory(
    Route, RouteStop, form=RouteStopForm,
    extra=1, can_delete=True
)

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['route', 'bus', 'route_type', 'vehicle_count', 'departure_time', 'return_time', 'days_of_week']
        widgets = {
            'route': forms.Select(attrs={'class': 'form-control'}),
            'bus': forms.Select(attrs={'class': 'form-control'}),
            'route_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'departure_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'return_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'days_of_week': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mon,Tue,Wed'}),
        }

class TripStopForm(forms.ModelForm):
    stop_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stop Name'}))
    
    class Meta:
        model = TripStop
        fields = ['order', 'arrival_time']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Seq'}),
            'arrival_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['stop_name'].initial = self.instance.stop.name

    def save(self, commit=True):
        instance = super().save(commit=False)
        stop_name = self.cleaned_data.get('stop_name')
        if stop_name:
            stop, created = Stop.objects.get_or_create(name=stop_name)
            instance.stop = stop
        if commit:
            instance.save()
        return instance

TripStopFormSet = inlineformset_factory(
    Trip, TripStop, form=TripStopForm,
    extra=1, can_delete=True
)

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['bus', 'source', 'destination', 'date', 'departure_time', 'status', 'is_special', 'driver_override']
        widgets = {
            'bus': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Starting Place'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_special': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'driver_override': forms.Select(attrs={'class': 'form-control'}),
        }
