from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import UserRegistrationForm, UserEditForm, AdminUserEditForm
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def admin_user_list(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    query = request.GET.get('q')
    users = User.objects.all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(id_number__icontains=query)
        )
    
    return render(request, 'accounts/admin_user_list.html', {'users': users, 'query': query})

@login_required
def admin_user_edit(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    user_to_edit = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user_to_edit.username} updated successfully.')
            return redirect('admin_user_list')
    else:
        form = AdminUserEditForm(instance=user_to_edit)
    
    return render(request, 'accounts/admin_user_edit.html', {'form': form, 'user_to_edit': user_to_edit})

@login_required
def admin_user_delete(request, pk):
    if not request.user.is_admin():
        return redirect('dashboard')
    
    user_to_delete = get_object_or_404(User, pk=pk)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_user_list')
        
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('admin_user_list')
    
    return render(request, 'accounts/admin_user_confirm_delete.html', {'user_to_delete': user_to_delete})
