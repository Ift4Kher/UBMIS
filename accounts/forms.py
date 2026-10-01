from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'id_number', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your ID'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and User.objects.filter(id_number__iexact=id_number).exists():
            raise forms.ValidationError("This University ID is already registered.")
        return id_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        # Automatically generate username from first and last name
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        base_username = slugify(f"{first_name}{last_name}").replace('-', '')
        
        # Ensure username is unique
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user.username = username
        
        if commit:
            user.save()
            if user.role == 'DRIVER':
                from fleet.models import DriverProfile
                DriverProfile.objects.create(user=user, license_number='PENDING')
        return user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'id_number', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and User.objects.filter(id_number__iexact=id_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This University ID is already registered to another user.")
        return id_number

class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'id_number', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number and User.objects.filter(id_number__iexact=id_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This University ID is already registered to another user.")
        return id_number
