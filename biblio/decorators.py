from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse


def admin_required(view_func):
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
            return redirect('login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Accès refusé. Seuls les administrateurs peuvent accéder à cette page.')
            return redirect('index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def user_or_admin_required(view_func):
    """
    Décorateur pour restreindre l'accès aux utilisateurs connectés (admin ou user)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def ajax_admin_required(view_func):
    """
    Décorateur pour les requêtes AJAX qui nécessitent des droits d'administrateur
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Non authentifié'}, status=401)
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            return JsonResponse({'error': 'Accès refusé. Droits administrateur requis.'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def check_permission(user, action):
    """
    Fonction utilitaire pour vérifier les permissions
    
    Args:
        user: L'utilisateur à vérifier
        action: L'action à effectuer ('view', 'create', 'edit', 'delete')
    
    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if not user.is_authenticated:
        return False
    
    if not hasattr(user, 'profile'):
        return False
    
    # Les admins ont tous les droits
    if user.profile.is_admin:
        return True
    
    # Les utilisateurs réguliers peuvent seulement voir
    if action == 'view':
        return True
    
    # Pour toutes les autres actions (create, edit, delete), seuls les admins ont accès
    return False
