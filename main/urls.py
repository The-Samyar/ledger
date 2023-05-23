from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index" ),
    path("transactions/", views.transactions, name="transactions" ),
    path("transactions/delete/<str:transaction_id>/", views.delete_transaction, name="delete transaction" ),
    path("transactions/edit/<str:transaction_id>/", views.edit_transaction, name="edit transaction" ),
    path("cards/", views.cards, name="cards"),
    path("cards/edit/<str:card_id>/", views.edit_card, name="edit cards"),
    path("cards/delete/<str:card_id>/", views.delete_card, name="delete cards"),
]