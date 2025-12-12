from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extension du modèle User de Django pour ajouter des informations supplémentaires
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('user', 'Utilisateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, verbose_name='Biographie')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur"""
        return self.role == 'admin'
    
    @property
    def is_regular_user(self):
        """Vérifie si l'utilisateur est un utilisateur régulier"""
        return self.role == 'user'
    
    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def to_dict(self):
        """Convertit le profil en dictionnaire"""
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'role_display': self.get_role_display(),
            'phone': self.phone,
            'address': self.address,
            'bio': self.bio,
            'avatar_url': self.avatar.url if self.avatar else None,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else None,
            'updated_at': self.updated_at.strftime("%d/%m/%Y %H:%M") if self.updated_at else None,
        }


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal pour créer automatiquement un profil lors de la création d'un utilisateur
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal pour sauvegarder le profil lors de la sauvegarde de l'utilisateur
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
