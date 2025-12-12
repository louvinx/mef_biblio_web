from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models_user import UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Formulaire d'inscription pour les nouveaux utilisateurs
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Adresse email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Nom'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': "Nom d'utilisateur"
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-10 pr-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/80 focus:border-transparent',
            'placeholder': 'Mot de passe'
        })
    )


class UserProfileForm(forms.ModelForm):
    """
    Formulaire pour modifier le profil utilisateur
    """
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Nom'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Adresse email'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'bio', 'avatar')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Numéro de téléphone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Adresse',
                'rows': 3
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Biographie',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class UserRoleForm(forms.ModelForm):
    """
    Formulaire pour modifier le rôle d'un utilisateur (admin uniquement)
    """
    class Meta:
        model = UserProfile
        fields = ('role',)
        widgets = {
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent'
            })
        }
