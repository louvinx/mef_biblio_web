"""
Context processor pour ajouter automatiquement les statistiques globales
à toutes les templates sans avoir à les passer manuellement dans chaque vue.

Pour l'utiliser, ajoutez ce fichier dans votre app (ex: biblio/context_processors.py)
et configurez-le dans settings.py
"""

from django.db.models import Count, Q
from .models import Book, Author, Category, Publisher


def global_stats(request):
    """
    Context processor qui ajoute les statistiques globales
    à toutes les templates automatiquement.
    
    Usage dans settings.py:
    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'biblio.context_processors.global_stats',
                ],
            },
        },
    ]
    """
    
    # Statistiques des livres en une seule requête
    books_stats = Book.objects.aggregate(
        total=Count('book_id'),
        available=Count('book_id', filter=Q(status='available')),
        borrowed=Count('book_id', filter=Q(status='borrowed')),
        reserved=Count('book_id', filter=Q(status='reserved')),
        pdf_count=Count('book_id', filter=Q(file__iendswith='.pdf')),
        epub_count=Count('book_id', filter=Q(file__iendswith='.epub')),
        mobi_count=Count('book_id', filter=Q(file__iendswith='.mobi')),
    )
    
    # Comptage des autres entités (3 requêtes simples et rapides)
    total_authors = Author.objects.count()
    total_categories = Category.objects.count()
    total_publishers = Publisher.objects.count()
    
    return {
        'stats': {
            'total': books_stats['total'] or 0,
            'available': books_stats['available'] or 0,
            'borrowed': books_stats['borrowed'] or 0,
            'reserved': books_stats['reserved'] or 0,
        },
        'total_authors': total_authors,
        'total_categories': total_categories,
        'total_publishers': total_publishers,
        'formats': {
            'pdf': books_stats['pdf_count'] or 0,
            'epub': books_stats['epub_count'] or 0,
            'mobi': books_stats['mobi_count'] or 0,
        },
    }