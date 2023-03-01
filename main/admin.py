from django.contrib import admin
from .models import Card, Transaction 

class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'bank_name', 'balance', 'user')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'card', 'target_card_number', 'target_account_type', 'date', 'amount', 'action', 'notes')
    readonly_fields = ('_transaction_id',)


admin.site.register(Card, CardAdmin)
admin.site.register(Transaction, TransactionAdmin)
