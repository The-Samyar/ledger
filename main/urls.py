from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path("", views.index, name="index" ),
    path("2/", views.index2, name="index" ),
    path("transactions/", views.transactions, name="transactions" ),
]