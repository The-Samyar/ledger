from django import forms
from . import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ["card", "target_card_number", "date_time", "amount", "notes", "action"]