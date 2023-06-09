from django import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ["card", "target_card_number", "date_time", "amount", "notes", "action"]

class CardForm(forms.ModelForm):
    class Meta:
        model = models.Card
        fields = ["card_number", "bank_name", "balance", "expiry_date"]

class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "email"]

class User_infoForm(forms.ModelForm):
    class Meta:
        model = models.User_info
        fields = ["phone_number", "gender", "dob"]

class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = ["first_name", "last_name", "card_number", "is_business"]

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]