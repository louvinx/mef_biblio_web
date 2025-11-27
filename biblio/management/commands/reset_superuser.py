from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Supprime tous les superutilisateurs et crée un nouveau superutilisateur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nom d\'utilisateur pour le nouveau superutilisateur (défaut: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email pour le nouveau superutilisateur (défaut: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin2025',
            help='Mot de passe pour le nouveau superutilisateur (défaut: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Supprimer tous les superutilisateurs existants
        superusers = User.objects.filter(is_superuser=True)
        count = superusers.count()
        
        if count > 0:
            self.stdout.write(self.style.WARNING(f'Suppression de {count} superutilisateur(s)...'))
            superusers.delete()
            self.stdout.write(self.style.SUCCESS(f'{count} superutilisateur(s) supprimé(s) avec succès'))
        else:
            self.stdout.write(self.style.NOTICE('Aucun superutilisateur à supprimer'))

        # Créer un nouveau superutilisateur
        self.stdout.write(self.style.WARNING(f'Création du nouveau superutilisateur "{username}"...'))
        
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS('✓ Nouveau superutilisateur créé avec succès!'))
            self.stdout.write(self.style.SUCCESS(f'  Nom d\'utilisateur: {username}'))
            self.stdout.write(self.style.SUCCESS(f'  Email: {email}'))
            self.stdout.write(self.style.SUCCESS(f'  Mot de passe: {password}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création du superutilisateur: {str(e)}'))
