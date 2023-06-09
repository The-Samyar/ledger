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

    path("profile/", views.profile, name="profile"),
    path("profile/add/profile-picture/", views.add_pic, name="add profile picture"),
    path("profile/delete/profile-picture/", views.delete_pic, name="delete profile picture"),
    path("profile/edit/password/", views.change_password, name="change password"),
    path("profile/add-contact/", views.add_contact, name="add new contact"),
    path("profile/edit-contact/<str:contact_id>/", views.edit_contact, name="edit contact info"),
    path("profile/delete-contact/<str:contact_id>/", views.delete_contact, name="delete contact"),

    path("login/", views.user_login, name="login"),
    path("sign-up/", views.user_signup, name="signup"),
    path("log-out/", views.user_logout, name="logout"),

]