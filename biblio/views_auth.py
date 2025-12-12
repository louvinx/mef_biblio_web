from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .forms_auth import UserRegistrationForm, CustomLoginForm, UserProfileForm, UserRoleForm
from .models_user import UserProfile
from .decorators import admin_required, user_or_admin_required


@admin_required
def register_view(request):
    """
    Vue pour l'inscription d'un nouvel utilisateur (Admin seulement)
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Le profil est créé automatiquement par le signal
            # On ne connecte PAS l'utilisateur car c'est un admin qui crée le compte
            messages.success(request, f'Le compte pour {user.username} a été créé avec succès.')
            return redirect('users_list')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'biblio/auth/register.html', {'form': form})


def login_view(request):
    """
    Vue pour la connexion d'un utilisateur
    """
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.username} !')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'biblio/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Vue pour la déconnexion d'un utilisateur
    """
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@user_or_admin_required
def profile_view(request):
    """
    Vue pour afficher et modifier le profil de l'utilisateur connecté
    """
    # S'assurer que le profil existe (pour éviter l'erreur 500 si le signal a échoué)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    return render(request, 'biblio/auth/profile.html', {
        'form': form,
        'profile': profile
    })


@admin_required
def users_list_view(request):
    """
    Vue pour afficher la liste de tous les utilisateurs (admin uniquement)
    """
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.select_related('profile').all()
    
    # Calculer les statistiques globales (avant filtrage)
    total_users = User.objects.count()
    total_admins = User.objects.filter(profile__role='admin').count()
    total_regulars = User.objects.filter(profile__role='user').count()
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    users = users.order_by('-date_joined')
    
    return render(request, 'biblio/auth/users_list.html', {
        'users': users,
        'search': search,
        'role_filter': role_filter,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_regulars': total_regulars,
    })


@admin_required
def user_detail_view(request, user_id):
    """
    Vue pour afficher les détails d'un utilisateur (admin uniquement)
    """
    user = get_object_or_404(User, pk=user_id)
    # S'assurer que le profil existe
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    return render(request, 'biblio/auth/user_detail.html', {
        'user_obj': user,
        'profile': profile
    })


@admin_required
@require_http_methods(["GET", "POST"])
def change_user_role_view(request, user_id):
    """
    Vue pour changer le rôle d'un utilisateur (admin uniquement)
    """
    user = get_object_or_404(User, pk=user_id)
    # S'assurer que le profil existe
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Empêcher un admin de changer son propre rôle
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas modifier votre propre rôle.')
        return redirect('users_list')
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Le rôle de {user.username} a été modifié avec succès.')
            return redirect('user_detail', user_id=user_id)
        else:
            messages.error(request, 'Erreur lors de la modification du rôle.')
    else:
        form = UserRoleForm(instance=profile)
    
    return render(request, 'biblio/auth/change_role.html', {
        'form': form,
        'user_obj': user,
        'profile': profile
    })


@admin_required
@require_http_methods(["POST"])
def delete_user_view(request, user_id):
    """
    Vue pour supprimer un utilisateur (admin uniquement)
    """
    user = get_object_or_404(User, pk=user_id)
    
    # Empêcher un admin de se supprimer lui-même
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('users_list')
    
    username = user.username
    user.delete()
    messages.success(request, f'L\'utilisateur {username} a été supprimé avec succès.')
    return redirect('users_list')


@login_required
def api_user_info(request):
    """
    API pour obtenir les informations de l'utilisateur connecté
    """
    if hasattr(request.user, 'profile'):
        return JsonResponse(request.user.profile.to_dict())
    else:
        return JsonResponse({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'role': 'user',
            'is_admin': False
        })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas d�connecter l'utilisateur
            messages.success(request, 'Votre mot de passe a été modifié avec succès !')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'biblio/auth/change_password.html', {'form': form})
