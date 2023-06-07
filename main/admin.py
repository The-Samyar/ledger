from django.contrib import admin
from .models import Card, Transaction, User_info, Contact

class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'bank_name', 'balance', 'user')

class User_infoAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'dob')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'card', 'target_card_number', 'target_account_type', 'date_time', 'amount', 'action', 'notes')
    readonly_fields = ('_transaction_id',)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'is_business', 'card_number')

admin.site.register(Card, CardAdmin)
admin.site.register(User_info, User_infoAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Contact, ContactAdmin)
