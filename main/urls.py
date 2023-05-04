from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index" ),
    path("transactions/", views.transactions, name="transactions" ),
    path("transactions/delete/<str:transaction_id>/", views.delete_transaction, name="delete transaction" ),
    path("transactions/edit/<str:transaction_id>/", views.edit_transaction, name="edit transaction" ),
]