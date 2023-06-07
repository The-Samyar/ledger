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
    
    date_time = models.DateTimeField(default=datetime.datetime.now)

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

class User_info(models.Model):
    GENDER_CHOICES = [
        ('m', 'Male'),
        ('f', 'Female'),
        ('n', 'Rather not say')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="extra_info")

    phone_number = models.CharField(null=True, blank=True, max_length=10)
    
    # age = models.IntegerField(null=True, blank=True)

    gender = models.CharField(null=True, blank=True, choices=GENDER_CHOICES, max_length=1)

    dob = models.DateField(null=True, blank=True)

    # profile_picture = models.CharField(max_length=30, default="")

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.DO_NOTHING, null=True)

    first_name = models.CharField(max_length=40)

    last_name = models.CharField(max_length=40, null=True, blank=True)

    card_number = models.CharField(max_length=16)

    is_business = models.BooleanField(default=False)

