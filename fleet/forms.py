from django import forms
from .models import Bus, DriverProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class InspectorUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'id_number', 'email', 'profile_picture', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Inspector ID'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and User.objects.filter(id_number__iexact=id_number).exists():
            raise forms.ValidationError("This University ID is already registered.")
        return id_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'INSPECTOR'
        if commit:
            user.save()
        return user

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['name', 'bus_number', 'bus_type', 'capacity', 'is_active', 'fitness_expiry', 'insurance_expiry']
        widgets = {
            'fitness_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional nickname'}),
            'bus_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DriverUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    license_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    assigned_bus = forms.ModelChoiceField(
        queryset=Bus.objects.filter(is_active=True),
        required=False,
        label="Assign Bus",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if DriverProfile.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("This license number is already registered.")
        return license_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'DRIVER'
        if commit:
            user.save()
            driver_profile = DriverProfile.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                license_expiry=self.cleaned_data['license_expiry']
            )
            
            # Handle Bus Assignment
            assigned_bus = self.cleaned_data.get('assigned_bus')
            if assigned_bus:
                from .models import BusDriverAssignment
                # Update or create assignment for this bus
                BusDriverAssignment.objects.update_or_create(
                    bus=assigned_bus,
                    defaults={'driver': driver_profile, 'is_active': True}
                )
        return user

class InspectorUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'id_number', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and User.objects.filter(id_number__iexact=id_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This University ID is already registered to another user.")
        return id_number

class DriverUpdateForm(forms.ModelForm):
    license_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    
    assigned_bus = forms.ModelChoiceField(
        queryset=Bus.objects.filter(is_active=True),
        required=False,
        label="Assign Bus",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'driver_profile'):
            self.fields['license_number'].initial = self.instance.driver_profile.license_number
            self.fields['license_expiry'].initial = self.instance.driver_profile.license_expiry
            
            # Pre-select assigned bus if any
            from .models import BusDriverAssignment
            try:
                assignment = BusDriverAssignment.objects.filter(driver=self.instance.driver_profile).first()
                current_assignment = BusDriverAssignment.objects.filter(driver=self.instance.driver_profile).last()
                if current_assignment:
                    self.fields['assigned_bus'].initial = current_assignment.bus
            except Exception:
                pass

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if DriverProfile.objects.filter(license_number=license_number).exclude(user=self.instance).exists():
            raise forms.ValidationError("This license number is already registered to another driver.")
        return license_number

    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'driver_profile'):
            profile = user.driver_profile
            profile.license_number = self.cleaned_data['license_number']
            profile.license_expiry = self.cleaned_data['license_expiry']
            profile.save()
            
            # Handle Bus Assignment
            assigned_bus = self.cleaned_data.get('assigned_bus')
            from .models import BusDriverAssignment
            
            # If a bus is selected
            if assigned_bus:
                BusDriverAssignment.objects.update_or_create(
                    bus=assigned_bus,
                    defaults={'driver': profile, 'is_active': True}
                )
            if assigned_bus:
                 # Remove this driver from other buses
                 BusDriverAssignment.objects.filter(driver=profile).exclude(bus=assigned_bus).delete()

        return user
