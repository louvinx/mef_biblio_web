from django import forms
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
import re
from datetime import date
from .models import Book, Author, Category, Publisher

class ISBNValidator:
    def __call__(self, value):
        if value:
            # Supprimer tous les tirets et espaces
            isbn = re.sub(r'[-\s]', '', value)
            if len(isbn) not in [10, 13]:
                raise forms.ValidationError(
                    _('L\'ISBN doit contenir 10 ou 13 chiffres'),
                    code='invalid_length'
                )
            if not isbn[:-1].isdigit() or (isbn[-1].upper() != 'X' and not isbn[-1].isdigit()):
                raise forms.ValidationError(
                    _('L\'ISBN ne doit contenir que des chiffres (et possiblement un X final pour ISBN-10)'),
                    code='invalid_characters'
                )

class BookForm(forms.ModelForm):
    book_type = forms.ChoiceField(
        choices=[('physical', 'Livre physique'), ('digital', 'Livre numérique')],
        widget=forms.RadioSelect(attrs={'class': 'book-type-radio'}),
        initial='physical',
        required=True,
        label=_("Type de livre")
    )
    
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'hidden'}),
        required=True,
        error_messages={'required': _('Veuillez sélectionner au moins un auteur')}
    )
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'hidden'}),
        required=True,
        error_messages={'required': _('Veuillez sélectionner au moins une catégorie')}
    )

    class Meta:
        model = Book
        fields = [
            'title', 'isbn', 'publisher', 'publication_year', 
            'pages', 'language', 'summary', 'total_copies',
            'available_copies', 'location', 'status', 'file', 'authors', 'categories'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Titre du livre',
                'minlength': '2',
                'maxlength': '200'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'ISBN (10 ou 13 chiffres)'
            }),
            'publisher': forms.Select(attrs={'class': 'hidden'}),
            'publication_year': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'min': '1800',
                'max': str(date.today().year)
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'min': '1'
            }),
            'language': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Langue du livre',
                'minlength': '2',
                'maxlength': '50'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Résumé du livre'
            }),
            'total_copies': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'min': '1'
            }),
            'available_copies': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'min': '0'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Emplacement physique du livre',
                'minlength': '2',
                'maxlength': '500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'accept': '.pdf,.epub,.mobi'
            }),
        }
        error_messages = {
            'title': {
                'required': _('Le titre est obligatoire'),
                'max_length': _('Le titre ne doit pas dépasser 200 caractères')
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['isbn'].validators.append(ISBNValidator())
        self.fields['publication_year'].validators.append(MinValueValidator(1800))
        self.fields['pages'].validators.append(MinValueValidator(1))
        self.fields['total_copies'].validators.append(MinValueValidator(1))
        self.fields['available_copies'].validators.append(MinValueValidator(0))

        # Déterminer le type de livre basé sur l'instance
        if self.instance and self.instance.pk:
            if self.instance.file:
                self.fields['book_type'].initial = 'digital'
            else:
                self.fields['book_type'].initial = 'physical'
        
        # Rendre certains champs conditionnels
        self.fields['file'].required = False
        self.fields['total_copies'].required = False
        self.fields['available_copies'].required = False

    def clean_publication_year(self):
        publication_year = self.cleaned_data.get('publication_year')
        if publication_year and publication_year > date.today().year:
            raise forms.ValidationError(
                _('L\'année de publication ne peut pas être dans le futur')
            )
        return publication_year

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 2:
            raise forms.ValidationError(
                _('Le titre doit contenir au moins 2 caractères')
            )
        return title

    def clean_language(self):
        language = self.cleaned_data.get('language')
        if language and len(language.strip()) < 2:
            raise forms.ValidationError(
                _('La langue doit contenir au moins 2 caractères')
            )
        return language

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location and len(location.strip()) < 2:
            raise forms.ValidationError(
                _('L\'emplacement doit contenir au moins 2 caractères')
            )
        return location

    def clean(self):
        cleaned_data = super().clean()
        book_type = cleaned_data.get('book_type')
        file = self.cleaned_data.get('file')
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')

        if book_type == 'digital':
            # Pour les livres numériques
            if not file and not (self.instance and self.instance.file):
                self.add_error('file', 'Un fichier est obligatoire pour les livres numériques')
            
            # Réinitialiser les champs physiques
            if total_copies:
                cleaned_data['total_copies'] = 1
            if available_copies:
                cleaned_data['available_copies'] = 1
            if cleaned_data.get('location'):
                cleaned_data['location'] = ''
                
        elif book_type == 'physical':
            # Pour les livres physiques
            if not total_copies:
                self.add_error('total_copies', 'Le nombre total d\'exemplaires est obligatoire pour les livres physiques')
            if available_copies is None:
                self.add_error('available_copies', 'Le nombre d\'exemplaires disponibles est obligatoire pour les livres physiques')
            
            # S'assurer qu'il n'y a pas de fichier
            if file:
                self.add_error('file', 'Un livre physique ne peut pas avoir de fichier')

        # Validation des exemplaires
        if total_copies and available_copies and available_copies > total_copies:
            self.add_error('available_copies', 'Le nombre d\'exemplaires disponibles ne peut pas être supérieur au nombre total')

        return cleaned_data

    def save(self, commit=True):
        book = super().save(commit=False)
        book_type = self.cleaned_data.get('book_type')
        
        if book_type == 'physical':
            # Pour les livres physiques, supprimer le fichier s'il existe
            if book.file:
                book.file.delete(save=False)
                book.file = None
        elif book_type == 'digital':
            # Pour les livres numériques, forcer 1 exemplaire
            book.total_copies = 1
            book.available_copies = 1
            book.location = ''
        
        if commit:
            book.save()
            self.save_m2m()
        
        return book

class AuthorForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
            'type': 'date',
            'max': date.today().isoformat()
        }),
        required=False,
        label=_("Date de naissance")
    )

    class Meta:
        model = Author
        fields = ['name', 'nationality', 'birth_date', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Nom de l\'auteur',
                'minlength': '2',
                'maxlength': '100'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Nationalité de l\'auteur',
                'minlength': '2',
                'maxlength': '50'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Biographie de l\'auteur'
            }),
        }
        error_messages = {
            'name': {
                'required': _('Le om est obligatoire'),
                'min_length': _('Le nom doit contenir au moins 2 caractères'),
                'max_length': _('Le nom ne doit pas dépasser 100 caractères')
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError(
                    _('Le nom doit contenir au moins 2 caractères')
                )
        return name


    def clean_nationality(self):
        nationality = self.cleaned_data.get('nationality')
        if nationality:
            nationality = nationality.strip()
            if len(nationality) < 2:
                raise forms.ValidationError(
                    _('La nationalité doit contenir au moins 2 caractères')
                )
        return nationality

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise forms.ValidationError(
                _('La date de naissance ne peut pas être dans le futur')
            )
        return birth_date

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Nom de la catégorie',
                'minlength': '2',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description de la catégorie'
            }),
        }
        error_messages = {
            'category_name': {
                'required': _('Le nom de la catégorie est obligatoire'),
                'min_length': _('Le nom de la catégorie doit contenir au moins 2 caractères'),
                'max_length': _('Le nom de la catégorie ne doit pas dépasser 100 caractères'),
                'unique': _('Une catégorie avec ce nom existe déjà')
            }
        }

    def clean_category_name(self):
        name = self.cleaned_data.get('category_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError(
                    _('Le nom de la catégorie doit contenir au moins 2 caractères')
                )
            
            # Vérifie si la catégorie existe déjà (ignore la casse)
            exists = Category.objects.filter(category_name__iexact=name)
            if self.instance.pk:  # Si c'est une mise à jour
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise forms.ValidationError(
                    _('Une catégorie avec ce nom existe déjà')
                )
        return name

class PhoneNumberValidator:
    def __call__(self, value):
        if value:
            # Accepte les formats: +XX-XXX-XXX-XXXX ou +XX XXX XXX XXXX
            if not re.match(r'^\+?[\d\s-]{10,20}$', value):
                raise forms.ValidationError(
                    _('Numéro de téléphone invalide. Format attendu: +XX-XXX-XXX-XXXX ou +XX XXX XXX XXXX'),
                    code='invalid_phone'
                )

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['publisher_name', 'address', 'phone', 'email']
        widgets = {
            'publisher_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'Nom de l\'éditeur',
                'minlength': '2',
                'maxlength': '150'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Adresse complète'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': '+XX-XXX-XXX-XXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
                'placeholder': 'email@editeur.com'
            }),
        }
        error_messages = {
            'publisher_name': {
                'required': _('Le nom de l\'éditeur est obligatoire'),
                'min_length': _('Le nom de l\'éditeur doit contenir au moins 2 caractères'),
                'max_length': _('Le nom de l\'éditeur ne doit pas dépasser 150 caractères')
            },
            'email': {
                'invalid': _('Adresse email invalide')
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].validators.append(PhoneNumberValidator())

    def clean_publisher_name(self):
        name = self.cleaned_data.get('publisher_name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError(
                    _('Le nom de l\'éditeur doit contenir au moins 2 caractères')
                )
            
            # Vérifie si l'éditeur existe déjà (ignore la casse)
            exists = Publisher.objects.filter(publisher_name__iexact=name)
            if self.instance.pk:  # Si c'est une mise à jour
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise forms.ValidationError(
                    _('Un éditeur avec ce nom existe déjà')
                )
        return name

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        
        if not phone and not email:
            raise forms.ValidationError(
                _('Vous devez fournir au moins un moyen de contact (téléphone ou email)')
            )
        return cleaned_data