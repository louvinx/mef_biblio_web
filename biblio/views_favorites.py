from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Favorite, Book
from django.views.decorators.http import require_http_methods


@login_required
def favorites_list_view(request):
    """
    Affiche la liste des livres favoris de l'utilisateur connecté.
    """
    search = request.GET.get('search', '')
    
    favorites = Favorite.objects.filter(user=request.user).select_related('book', 'book__publisher')
    
    if search:
        favorites = favorites.filter(
            Q(book__title__icontains=search) |
            Q(book__authors__name__icontains=search) |
            Q(book__isbn__icontains=search)
        ).distinct()
    
    # Récupérer les livres depuis les favoris
    favorite_books = [fav.book for fav in favorites]
    
    context = {
        'favorites': favorites,
        'favorite_books': favorite_books,
        'search': search,
        'total_favorites': favorites.count(),
    }
    
    return render(request, 'biblio/favorites/favorites_list.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_favorite_view(request, book_id):
    """
    Ajoute ou retire un livre des favoris de l'utilisateur.
    Retourne une réponse JSON pour les requêtes AJAX.
    """
    book = get_object_or_404(Book, book_id=book_id)
    
    # Vérifier si le livre est déjà dans les favoris
    favorite = Favorite.objects.filter(user=request.user, book=book).first()
    
    if favorite:
        # Retirer des favoris
        favorite.delete()
        is_favorite = False
        message = f'"{book.title}" a été retiré de vos favoris.'
    else:
        # Ajouter aux favoris
        Favorite.objects.create(user=request.user, book=book)
        is_favorite = True
        message = f'"{book.title}" a été ajouté à vos favoris.'
    
    # Si c'est une requête AJAX, retourner JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message,
            'favorites_count': request.user.favorites.count()
        })
    
    # Sinon, ajouter un message et rediriger
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
@require_http_methods(["POST"])
def remove_favorite_view(request, favorite_id):
    """
    Retire un livre des favoris (depuis la page des favoris).
    """
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    book_title = favorite.book.title
    favorite.delete()
    
    messages.success(request, f'"{book_title}" a été retiré de vos favoris.')
    return redirect('favorites_list')


@login_required
def check_favorite_status(request, book_id):
    """
    API endpoint pour vérifier si un livre est dans les favoris.
    """
    is_favorite = Favorite.objects.filter(user=request.user, book_id=book_id).exists()
    
    return JsonResponse({
        'is_favorite': is_favorite,
        'favorites_count': request.user.favorites.count()
    })
