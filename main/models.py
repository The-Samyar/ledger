import datetime
from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    card_number = models.CharField(max_length=22)

    bank_name = models.CharField(max_length=20)

    balance = models.IntegerField()

    expiry_date = models.DateField(blank=True, null=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cards')
    
    def __str__(self):
        return f"{self.user} - {self.card_number}"

class Transaction(models.Model):
    ACTION_CHOICES = [
        ('withdraw', 'Withdraw'),
        ('deposit', 'Deposit')
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('person', 'Person'),
        ('company', 'Company')
    ]

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='transactions')

    target_card_number = models.CharField(max_length=22, blank=True, null=True)

    target_account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES,blank=True, null=True)
    
    date = models.DateField()

    amount = models.IntegerField()

    action = models.CharField(max_length=8, choices=ACTION_CHOICES)
    
    notes = models.CharField(
        blank=True,
        max_length=200)

    # read-only field
    _transaction_id = models.CharField(unique=True, max_length=50)

    def save(self, *args, **kwargs):
        self._transaction_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(self.card)[-4:]
        super(Transaction, self).save(*args, **kwargs)

    @property
    def transaction_id(self):
        return self._transaction_id

