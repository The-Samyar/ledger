from django import forms
from . import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ["card", "target_card_number", "date_time", "amount", "notes", "action"]

class CardForm(forms.ModelForm):
    class Meta:
        model = models.Card
        fields = ["card_number", "bank_name", "balance", "expiry_date"]