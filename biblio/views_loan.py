from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Loan, Book
from .forms_loan import LoanForm
from .decorators import admin_required

@login_required
def my_loans(request):
    """
    Vue pour afficher l'historique des prêts de l'utilisateur connecté
    """
    loans = Loan.objects.filter(user=request.user).order_by('-request_date')
    return render(request, 'biblio/loans/my_loans.html', {'loans': loans})

@admin_required
def loan_list(request):
    """
    Vue pour afficher tous les prêts (admin seulement)
    """
    loans = Loan.objects.all().order_by('-request_date')
    return render(request, 'biblio/loans/loan_list.html', {'loans': loans})

@login_required
def create_loan(request):
    """
    Vue pour créer un nouveau prêt
    """
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.status = 'ACTIVE'
            if not loan.loan_date:
                loan.loan_date = timezone.now().date()
            loan.save()
            
            # Mettre à jour le statut du livre
            book = loan.book
            book.status = 'borrowed'
            book.save()
            
            messages.success(request, 'Le prêt a été créé avec succès.')
            # Rediriger vers la liste appropriée selon le rôle
            if hasattr(request.user, 'profile') and request.user.profile.is_admin:
                return redirect('loan_list')
            else:
                return redirect('my_loans')
    else:
        initial_data = {'loan_date': timezone.now().date()}
        
        # Pré-sélectionner le livre
        book_id = request.GET.get('book')
        if book_id:
            initial_data['book'] = book_id
            
        # Pré-sélectionner l'utilisateur (pour le formulaire admin qui a un champ user)
        # Note: Si LoanForm exclut 'user' pour les non-admins, ceci sera simplement ignoré par le formulaire s'il n'y a pas le champ
        initial_data['user'] = request.user.id
        
        form = LoanForm(initial=initial_data)
    
    return render(request, 'biblio/loans/create_loan.html', {'form': form})

@login_required
def return_loan(request, loan_id):
    """
    Vue pour marquer un prêt comme retourné
    Les utilisateurs peuvent retourner leurs propres livres
    Les admins peuvent retourner n'importe quel livre
    """
    loan = get_object_or_404(Loan, pk=loan_id)
    
    # Vérifier que l'utilisateur a le droit de retourner ce livre
    is_admin = hasattr(request.user, 'profile') and request.user.profile.is_admin
    is_owner = loan.user == request.user
    
    if not (is_admin or is_owner):
        messages.error(request, "Vous n'avez pas la permission de retourner ce livre.")
        return redirect('my_loans')
    
    if request.method == 'POST':
        loan.status = 'RETURNED'
        loan.return_date = timezone.now().date()
        loan.save()
        
        # Libérer le livre
        book = loan.book
        book.status = 'available'
        book.save()
        
        messages.success(request, f'Le livre "{book.title}" a été marqué comme retourné.')
        
        # Redirection selon le rôle
        if is_admin:
            return redirect('loan_list')
        else:
            return redirect('my_loans')
    
    return render(request, 'biblio/loans/return_confirm.html', {'loan': loan})
