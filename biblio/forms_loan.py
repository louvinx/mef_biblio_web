from django import forms
from .models import Loan, Book
from django.contrib.auth.models import User
from datetime import date

class LoanForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(status='available', file__isnull=True) | Book.objects.filter(status='available', file=''),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent'}),
        label="Livre"
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent'}),
        label="Utilisateur"
    )
    loan_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent'}),
        label="Date de prêt",
        initial=date.today
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent'}),
        label="Date de retour prévue (optionnel)"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent', 'rows': 3}),
        label="Notes"
    )

    class Meta:
        model = Loan
        fields = ['book', 'user', 'loan_date', 'due_date', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on édite un prêt existant, on doit pouvoir voir le livre même s'il est emprunté
        if self.instance and self.instance.pk:
            self.fields['book'].queryset = Book.objects.all()

    def clean_loan_date(self):
        loan_date = self.cleaned_data.get('loan_date')
        if loan_date and loan_date > date.today():
            raise forms.ValidationError("La date de prêt ne peut pas être dans le futur.")
        return loan_date

    def clean(self):
        cleaned_data = super().clean()
        loan_date = cleaned_data.get('loan_date')
        due_date = cleaned_data.get('due_date')

        if loan_date and due_date:
            if due_date <= loan_date:
                raise forms.ValidationError("La date de retour prévue doit être postérieure à la date de prêt.")
            
            # La date de retour ne peut pas être dans le passé (pour les nouveaux prêts)
            if not self.instance.pk and due_date < date.today():
                raise forms.ValidationError("La date de retour prévue ne peut pas être dans le passé.")
        
        # Vérifier la disponibilité du livre
        book = cleaned_data.get('book')
        if book and not self.instance.pk:
            # Vérifier si le livre est toujours disponible
            if book.status != 'available':
                raise forms.ValidationError(f"Le livre '{book.title}' n'est plus disponible.")
            
            # Vérifier les copies si applicable
            if book.available_copies is not None and book.available_copies < 1:
                 raise forms.ValidationError(f"Il n'y a plus d'exemplaires disponibles pour '{book.title}'.")

        return cleaned_data
