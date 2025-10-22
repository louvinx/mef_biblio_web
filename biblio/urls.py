from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/books/', views.api_books, name='api_books'),
    path('api/books/<int:book_id>/', views.api_get_book, name='api_get_book'),
    path('api/books/<int:book_id>/download/', views.api_download_book, name='api_download_book'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/authors/', views.api_authors, name='api_authors'),
    path('api/publishers/', views.api_publishers, name='api_publishers'),
    
    # Gestion des fichiers PDF
    path('books/<int:book_id>/download/', views.download_book, name='download_book'),
    path('books/<int:book_id>/read/', views.read_book, name='read_book'),


    
    # Form views for authors
    path('authors/add/', views.add_author, name='add_author'),
    path('authors/<int:author_id>/edit/', views.edit_author, name='edit_author'),
    path('authors/<int:author_id>/delete/', views.delete_author, name='delete_author'),
    
    # Form views for categories
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Form views for publishers
    path('publishers/add/', views.add_publisher, name='add_publisher'),
    path('publishers/<int:publisher_id>/edit/', views.edit_publisher, name='edit_publisher'),
    path('publishers/<int:publisher_id>/delete/', views.delete_publisher, name='delete_publisher'),
    
    # Form views for books
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('books/', views.book_list, name='book_list'),

    path('books/export/excel/', views.export_books_excel, name='export_books_excel'),
    path('books/export/pdf/', views.export_books_pdf, name='export_books_pdf'),
    path('books/export/word/', views.export_books_word, name='export_books_word'),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)