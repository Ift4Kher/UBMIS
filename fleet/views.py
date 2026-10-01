from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Bus, DriverProfile
from .forms import BusForm, DriverUserForm

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_inspector(user):
    # Use the model method if available, fallback to role check
    if not user.is_authenticated:
        return False
    return user.is_superuser or (hasattr(user, 'role') and user.role == 'INSPECTOR')

@login_required
@user_passes_test(is_admin)
def bus_list(request):
    buses = Bus.objects.all()
    return render(request, 'fleet/bus_list.html', {'buses': buses})

@login_required
@user_passes_test(is_admin)
def bus_create(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus created successfully.')
            return redirect('bus_list')
    else:
        form = BusForm()
    return render(request, 'fleet/bus_form.html', {'form': form, 'title': 'Add Bus'})

@login_required
@user_passes_test(is_admin)
def bus_update(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully.')
            return redirect('bus_list')
    else:
        form = BusForm(instance=bus)
    return render(request, 'fleet/bus_form.html', {'form': form, 'title': 'Edit Bus'})

@login_required
@user_passes_test(is_admin)
def bus_delete(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        bus.delete()
        messages.success(request, 'Bus deleted successfully.')
        return redirect('bus_list')
    return render(request, 'fleet/bus_confirm_delete.html', {'bus': bus})

# Driver Views (Similar structure)
@login_required
@user_passes_test(is_admin)
def driver_list(request):
    drivers = DriverProfile.objects.prefetch_related(
        'busdriverassignment_set__bus__schedule_set__route'
    ).all()
    return render(request, 'fleet/driver_list.html', {'drivers': drivers})

@login_required
@user_passes_test(is_admin)
def driver_create(request):
    if request.method == 'POST':
        form = DriverUserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver profile created successfully.')
            return redirect('driver_list')
    else:
        form = DriverUserForm()
    return render(request, 'fleet/driver_form.html', {'form': form, 'title': 'Add Driver'})

# Inspector Management Views
from .forms import InspectorUserForm, InspectorUpdateForm, DriverUpdateForm
from django.contrib.auth import get_user_model

@login_required
@user_passes_test(is_admin)
def inspector_list(request):
    User = get_user_model()
    # Filter users who have the role INSPECTOR
    inspectors = User.objects.filter(role='INSPECTOR')
    return render(request, 'fleet/inspector_list.html', {'inspectors': inspectors})

@login_required
@user_passes_test(is_admin)
def inspector_create_account(request):
    if request.method == 'POST':
        form = InspectorUserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inspector account created successfully.')
            return redirect('inspector_list')
    else:
        form = InspectorUserForm()
    return render(request, 'fleet/inspector_form.html', {'form': form, 'title': 'Add Inspector'})

@login_required
@user_passes_test(is_admin)
def inspector_update(request, pk):
    User = get_user_model()
    inspector = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = InspectorUpdateForm(request.POST, request.FILES, instance=inspector)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inspector account updated successfully.')
            return redirect('inspector_list')
    else:
        form = InspectorUpdateForm(instance=inspector)
    return render(request, 'fleet/inspector_form.html', {'form': form, 'title': 'Edit Inspector'})

@login_required
@user_passes_test(is_admin)
def inspector_delete(request, pk):
    User = get_user_model()
    inspector = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        inspector.delete() # Cascade deletes profile if any
        messages.success(request, 'Inspector account deleted successfully.')
        return redirect('inspector_list')
    return render(request, 'fleet/confirm_delete.html', {'object': inspector, 'type': 'Inspector'})

# Driver Update/Delete
@login_required
@user_passes_test(is_admin)
def driver_update(request, pk):
    driver_profile = get_object_or_404(DriverProfile, pk=pk)
    user = driver_profile.user
    if request.method == 'POST':
        form = DriverUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver profile updated successfully.')
            return redirect('driver_list')
    else:
        form = DriverUpdateForm(instance=user)
    return render(request, 'fleet/driver_form.html', {'form': form, 'title': 'Edit Driver'})

@login_required
@user_passes_test(is_admin)
def driver_delete(request, pk):
    driver_profile = get_object_or_404(DriverProfile, pk=pk)
    user = driver_profile.user
    if request.method == 'POST':
        user.delete() # Deleting user also deletes profile due to CASCADE
        messages.success(request, 'Driver account deleted successfully.')
        return redirect('driver_list')
    return render(request, 'fleet/confirm_delete.html', {'object': user, 'type': 'Driver'})

# Inspection Views
from .models import BusInspection
from .inspection_forms import InspectionForm

@login_required
@user_passes_test(is_inspector)
def inspection_list(request):
    inspections = BusInspection.objects.all().order_by('-inspection_date')
    return render(request, 'fleet/inspection_list.html', {'inspections': inspections})

@login_required
@user_passes_test(is_inspector)
def inspection_create(request):
    if request.method == 'POST':
        form = InspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.inspector = request.user
            inspection.save()
            messages.success(request, 'Bus inspection submitted successfully. Report generated.')
            return redirect('inspection_report_detail', pk=inspection.pk)
    else:
        # Auto-fill info in context for Read-Only display in template
        initial_info = {
            'inspector_name': request.user.get_full_name() or request.user.username,
            'inspector_id': request.user.id,
            'date_time': timezone.now(),
        }
        form = InspectionForm()
        
    # V7.0 Atomic Logic: Pre-process fields to prevent template-tag splitting by formatters
    import json
    critical_fields = ['doc_registration', 'doc_fitness', 'mech_brake', 'mech_steering', 'safe_fire_extinguisher', 'safe_emergency_exit']
    exclude_fields = ['bus', 'location', 'remarks', 'photo_evidence', 'next_inspection_date']
    
    evaluation_items = []
    field_errors = {}
    
    for field in form:
        if field.errors:
            field_errors[field.name] = field.errors[0]
            
        if field.name not in exclude_fields:
            evaluation_items.append({
                'name': field.name,
                'label': field.label,
                'id_for_label': field.id_for_label,
                'value': field.value() if callable(field.value) else field.value,
            })

    return render(request, 'fleet/inspection_form.html', {
        'form': form, 
        'title': 'Professional Bus Inspection',
        'now': timezone.now(),
        'evaluation_items': evaluation_items,
        'critical_fields_json': json.dumps(critical_fields),
        'field_errors_json': json.dumps(field_errors),
        'exclude_fields': exclude_fields
    })

@login_required
@user_passes_test(is_inspector)
def inspection_report_detail(request, pk):
    inspection = get_object_or_404(BusInspection.objects.select_related('bus', 'inspector'), pk=pk)
    
    # Calculate display name in view to avoid template tag splitting issues
    inspector_name = inspection.inspector.get_full_name()
    if not inspector_name:
        inspector_name = inspection.inspector.username
        
    context = {
        'inspection': inspection,
        'inspector_name': inspector_name,
    }
    return render(request, 'fleet/inspection_report.html', context)

@login_required
@user_passes_test(is_admin)
def inspection_delete(request, pk):
    inspection = get_object_or_404(BusInspection, pk=pk)
    if request.method == 'POST':
        inspection.delete()
        messages.success(request, 'Inspection record deleted successfully.')
        return redirect('inspection_list')
    return render(request, 'fleet/confirm_delete.html', {'object': inspection, 'type': 'Inspection Record'})
