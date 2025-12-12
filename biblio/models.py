from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
import os

# Import du modèle UserProfile
from .models_user import UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def book_upload_path(instance, filename):
    return f'books/{instance.book_id}/{filename}'

def book_cover_path(instance, filename):
    return f'books/{instance.book_id}/covers/{filename}'

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

    def to_dict(self):
        return {
            'id': self.category_id,
            'name': self.category_name,
            'description': self.description
        }

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            'id': self.author_id,
            'name': self.name,
            'full_name': f"Auteur: {self.name}",
            'nationality': self.nationality,
            'biography': self.biography
        }

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    publisher_name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.publisher_name

    def to_dict(self):
        return {
            'id': self.publisher_id,
            'name': self.publisher_name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email
        }

class Book(models.Model):
    GENRE_CHOICES = [
        ('ROM', 'Roman'),
        ('POL', 'Policier'),
        ('SF', 'Science-Fiction'),
        ('FAN', 'Fantastique'),
        ('HIS', 'Historique'),
        ('BIO', 'Biographie'),
        ('ESS', 'Essai'),
    ]

    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('borrowed', 'Emprunté'),
        ('reserved', 'Réservé'),
        ('maintenance', 'Maintenance'),
    ]

    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    publication_year = models.IntegerField(blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='français')
    summary = models.TextField(blank=True, null=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    location = models.CharField(max_length=500, blank=True, null=True)
    cover_image = models.ImageField(upload_to=book_cover_path, blank=True, null=True)
    file = models.FileField(
        upload_to=book_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'epub', 'mobi'])]
    )
    status = models.CharField(max_length=100, default="available", choices=STATUS_CHOICES)
    authors = models.ManyToManyField(Author, through='BookAuthor')
    categories = models.ManyToManyField(Category, through='BookCategory')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    
    @property
    def is_digital(self):
        """Retourne True si c'est un livre numérique"""
        return bool(self.file and self.file.name)

    @property
    def is_physical(self):
        """Retourne True si c'est un livre physique"""
        return not self.is_digital

    @property
    def file_extension(self):
        """Retourne l'extension du fichier"""
        if self.file and self.file.name:
            return os.path.splitext(self.file.name)[1].lower()
        return None

    @property
    def file_type(self):
        """Retourne le type de fichier"""
        ext = self.file_extension
        if ext == '.pdf':
            return 'PDF'
        elif ext == '.epub':
            return 'EPUB'
        elif ext == '.mobi':
            return 'MOBI'
        return None

    def to_dict(self):
        return {
            'id': self.book_id,
            'title': self.title,
            'isbn': self.isbn,
            'publication_year': self.publication_year,
            'pages': self.pages,
            'language': self.language,
            'summary': self.summary,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'location': self.location,
            'cover_image': self.cover_image.url if self.cover_image else None,
            'file_url': self.file.url if self.file else None,
            'status': self.status,
            'is_digital': self.is_digital,
            'file_type': self.file_type,
            'publisher': self.publisher.to_dict() if self.publisher else None,
            'categories': [cat.to_dict() for cat in self.categories.all()],
            'authors': [author.to_dict() for author in self.authors.all()],
            'created_at': self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else None,
            'updated_at': self.updated_at.strftime("%d/%m/%Y %H:%M") if self.updated_at else None
        }

class BookCategory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'category')

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    contribution_order = models.IntegerField(default=1)
    contribution_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'author')

class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('ACTIVE', 'En cours'),
        ('RETURNED', 'Retourné'),
        ('OVERDUE', 'En retard'),
        ('REJECTED', 'Rejeté'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    request_date = models.DateTimeField(auto_now_add=True)
    loan_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.loan_date and not self.due_date:
            # Par défaut, prêt de 14 jours
            self.due_date = self.loan_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        if self.status == 'ACTIVE' and self.due_date and self.due_date < timezone.now().date():
            return True
        return False


class Favorite(models.Model):
    """
    Modèle pour gérer les livres favoris des utilisateurs.
    Permet aux utilisateurs de marquer des livres comme favoris pour un accès rapide.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'book')  # Un livre ne peut être favori qu'une fois par utilisateur
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-added_at']  # Les plus récents en premier
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
