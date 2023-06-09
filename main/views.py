from django.shortcuts import render, redirect
from django.contrib.auth import models, login, logout, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.core import serializers

import json
import datetime
from PIL import Image
from pathlib import Path
import os

from . import models, forms

BALANCE_BANK_COLORS = ["rgb(133, 105, 241)",
                       "rgb(164, 101, 241)",
                       "rgb(101, 143, 241)",
                       "rgb(208, 46, 203)",
                       "rgb(226, 141, 181)",
                       "rgb(71, 92, 230)",
                        ]

MONTHS = ["January","February","March","April","May","June","July","August","September", "October", "November", "December"]

@login_required
def index(request):
    if request.method == 'GET':
        user = request.user
        user_cards = user.cards.all()
        transactions = models.Transaction.objects.filter(card__in=user_cards).order_by('-date_time')
        deposits = transactions.filter(action='deposit')
        withdraws = transactions.filter(action='withdraw')

        # Meta data for doghnut chart
        doughnutChartData = {
            "labels": list(user_cards.values_list('bank_name',flat=True)),
            "datasets" : [{
                    "label": "Balance",
                    "data": list(user_cards.values_list('balance',flat=True)),
                    "backgroundColor": BALANCE_BANK_COLORS[:len(user_cards)],
                    "hoverOffset": 20,
                    },],
        }

        # Jsonifies the meta data
        doughnutChartData = json.dumps(doughnutChartData)

        # Meta data preparation for line chart. The total amount is calculated monthly starting from 6 months ago
        now = datetime.datetime.now()
        labels = []
        total_withdraws = []
        total_deposits = []
        for i in range(6):
            desired_month = ((now.month-1) + 7 + i) % 12
            labels.append(MONTHS[desired_month])
            total_withdraws.append(withdraws.filter(date_time__year=now.year, date_time__month=desired_month+1).aggregate(total=Sum('amount', default=0))['total'])
            total_deposits.append(deposits.filter(date_time__year=now.year, date_time__month=desired_month+1).aggregate(total=Sum('amount',default=0))['total'])

        lineChartData = {
            "labels": labels,
            "datasets" : [{
                    "label": "Last 6 months expenses",
                    "backgroundColor": "hsl(267, 83%, 67%)",
                    "borderColor": "hsl(267, 83%, 67%)",
                    "data": total_withdraws,
                    },
                    {
                    "label": "Last 6 months earnings",
                    "backgroundColor": "hsl(217, 57%, 51%)",
                    "borderColor": "hsl(217, 57%, 51%)",
                    "data": total_deposits,
                    },],
        }

        lineChartData = json.dumps(lineChartData)

        # User profile picture. If not found sends a default picture's directory address
        image_address = f"main/static/main/img/users/{user.username}/profile.webp"
        if os.path.exists(image_address):
            image_address = f"main/img/users/{user.username}/profile.webp"
        else:
            image_address = f"main/img/default_profile.svg"

        context = {
            'user' : user,
            'deposits' : deposits[:3],
            'withdraws' : withdraws[:3],
            'balance' : user.cards.aggregate(total=Sum('balance')),
            'incomes' : deposits.aggregate(total=Sum('amount')),
            'expenses' : withdraws.aggregate(total=Sum('amount')),
            'cards' : user_cards,
            'doughnutChartData' : doughnutChartData,
            'lineChartData' : lineChartData,
            'user_profile_picture' : image_address
        }

        return render(request, "index.html", context)

@login_required
def transactions(request):
    user = request.user
    if request.method == 'GET':
        context = {
            'user' : user,
            'transactions' : models.Transaction.objects.filter(card__in=user.cards.all()).order_by('-date_time')
        }
        return render(request, "transactions.html", context)
    
    elif request.method == 'POST':
        # Submits a new transaction
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            user_card = form.cleaned_data['card']
            if form.cleaned_data['action'] == 'deposit':
                user_card.balance += form.cleaned_data['amount']
            else:
                user_card.balance -= form.cleaned_data['amount']
            user_card.save(), form.save()
            print("Transaction successfully added")
        else:
            print("Transaction was not added")
            print(form.errors)
        return redirect('/transactions/')

    
@login_required
def edit_transaction(request, transaction_id):
    user = request.user
    if request.method == 'POST':
        # Checks if the transaction belongs to the user
        instance = models.Transaction.objects.get(_transaction_id=transaction_id, card__in=user.cards.all())
        if instance:
            form = forms.TransactionForm(
                request.POST,
                instance = instance
                )
            if form.is_valid() == True:
                # Since transaction is being edited, balances of cards need to be changed too
                initial_card = models.Card.objects.get(id=form['card'].initial)
                if form['action'].initial == 'deposit':
                    initial_card.balance -= form['amount'].initial
                else:
                    initial_card.balance += form['amount'].initial
                initial_card.save()
                
                edited_card = models.Card.objects.get(id=form.cleaned_data['card'].id)
                if form.cleaned_data['action'] == 'deposit':
                    edited_card.balance += form.cleaned_data['amount']
                else:
                    edited_card.balance -= form.cleaned_data['amount']
                edited_card.save()
                form.save() 
                print("Transaction was succseefully edited")
            else:
                print(form.errors)
        else:
            print("Transaction was not found")
        return redirect('/transactions/')

@login_required
def delete_transaction(request, transaction_id):
    user = request.user
    target_transaction = models.Transaction.objects.get(_transaction_id=transaction_id, cards__in=user.cards.all())
    if target_transaction:
        user_card = target_transaction.card
        if target_transaction.action == 'deposit':
            user_card.balance -= target_transaction.amount
        else:
            user_card.balance += target_transaction.amount
        target_transaction.delete(), user_card.save()
        print("Transaction was successfully deleted")
    else:
        print("Transaction was not found")
    return redirect('/transactions/')

@login_required
def cards(request):
    user = request.user
    if request.method == 'GET':
        today = datetime.datetime.now()
        user_cards = user.cards.all()

        # The date format shown for x axis labels of the line chart
        date_format = "%m %d"

        # Line chart meta data
        current_balance = user_cards.aggregate(total_balance=Sum('balance', default=0))['total_balance']
        labels = [today.strftime(date_format)]
        user_transactions = models.Transaction.objects.filter(card__in=user_cards)
        
        # datasets holds the info for each card, but the 0th dataset in datasets is the total balance
        # total balance dataset
        datasets = [{
                    "label": "Total balance",
                    "backgroundColor": "hsl(0, 0%, 100%)",
                    "borderColor": "hsl(0, 0%, 100%)",
                    "data": [current_balance],
                    },
                    ]
        
        # user cards datasets
        for k in range(len(user_cards)):
            datasets.append({
                "label": user_cards[k].bank_name,
                "backgroundColor": BALANCE_BANK_COLORS[k],
                "borderColor": BALANCE_BANK_COLORS[k],
                "data": [user_cards[k].balance,],
                })

        # The loop goes back day by day for a whole month and each time the balance of all cards as well as the total balance are updated. The idea of going back day by day roots from the fact that the balance of previous day depends on the transactions happened today. So by reversing today's transactions, balance of yesterday can be calculated
        for i in range(1,30):
            target_date = today - datetime.timedelta(days=i)

            labels.append(target_date.strftime(date_format))

            target_date = target_date + datetime.timedelta(days=1)
            daily_transactions = user_transactions.filter(date_time__year=target_date.year, date_time__month=target_date.month,date_time__day=target_date.day)
            total_balance = 0
            for j in range(1,len(datasets)):
                transactions_sums = daily_transactions.aggregate(
                    deposits_sum=Sum('amount', filter=(Q(action='deposit') & Q(card=user_cards.get(bank_name=datasets[j]['label']))), default=0),
                    withdraws_sum=Sum('amount', filter=(Q(action='withdraw') & Q(card=user_cards.get(bank_name=datasets[j]['label']))), default=0)
                    )

                card_balance = datasets[j]['data'][-1] - transactions_sums['deposits_sum'] + transactions_sums['withdraws_sum']

                datasets[j]['data'].append(card_balance)

                # to update 0th dataset
                total_balance += card_balance

            datasets[0]["data"].append(total_balance)

        # Since the algorithm went back day by day, the calculated balances are in reversed order, so their order is reversed
        for dataset in datasets:
            dataset["data"].reverse()
        labels.reverse()
        
        lineChartData = {
            "labels": labels,
            "datasets" : datasets,
        }

        # contains the destination card number that has the highest transaction rate 
        purchase_report = user_transactions.values(
            'target_card_number'
            ).annotate(
            count=Count('card')
            ).annotate(
            sum=Sum('amount',filter=Q(action='deposit'),default=0)-Sum('amount',filter=Q(action='withdraw'),default=0)
            ).order_by(
            '-count'
            )

        context = {
            'cards' : list(zip(user.cards.all(), BALANCE_BANK_COLORS)),
            'cards_json' : serializers.serialize("json", user.cards.all()),
            'lineChartData' : json.dumps(lineChartData),
            'purchase_report' : purchase_report[:2],
            }
        
        return render(request, "cards.html", context=context)
    
    elif request.method == 'POST':
        # adds new card
        form = forms.CardForm(request.POST)
        if form.is_valid():
            new_card = form.save(commit=False)
            new_card.user = user
            new_card.save()
            print("Card was successfully added")
        else:
            print("Cards was not added")
            print(form.errors)

        return redirect('/cards/')
    
@login_required
def edit_card(request, card_id):
    if request.method == 'POST':
        user = request.user
        instance = models.Card.objects.get(user=user, id=card_id)
        if instance:
            form = forms.CardForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                print("Card was edited successfully")
            else:
                print("Card was not edited")
                print(form.errors)
        else:
            print("Cards was not found")
        return redirect('/cards/')

@login_required
def delete_card(request, card_id):
    if request.method == 'GET':
        user = request.user
        card = models.Card.objects.get(user=user, id=card_id)
        if card:
            print("Card was deleted")
            card.delete()
        else:
            print("Card was not found")
        return redirect('/cards/')

@login_required
def profile(request):
    user = request.user
    if request.method == 'GET':
        context = {
            'user_info' : user,
            'user_contacts': user.contacts.all(),
            'genders' : models.User_info.gender.field.choices,
        }

        return render(request, 'profile.html', context=context)
    
    # edits user info
    elif request.method == 'POST':
        # handles the information related to django's User model
        user_form = forms.UserForm(request.POST, instance=user)

        # handles the info related to User_info model
        user_info_form = forms.User_infoForm(request.POST, instance=user.extra_info)

        if user_form.is_valid():
            if user_info_form.is_valid():
                user_form.save()
                user_info_form.save()
                print("User information was edited successfully")
                return redirect("/profile/")
            else:
                print("User information was not edited")
                print(user_info_form.errors)
                return redirect("/profile/")
        else:
            print("User information was not edited")
            print(user_form.errors)
            return redirect("/profile/")

@login_required
def add_pic(request):
    user = request.user
    if request.method == 'POST':
        image_file = request.FILES['profile_picture']

        image_address = f"main/static/main/img/users/{user.username}/"

        try:
            Path(image_address).mkdir(parents=True)
            print("path created")
        except FileExistsError:
            print("path exists")
        
        image = Image.open(image_file)
        image.save(image_address + "profile.webp")
        image.close()

        return redirect("/profile/")

@login_required
def delete_pic(request):
    user = request.user
    if request.method == 'GET':
        image_address = f"main/static/main/img/users/{user.username}/profile.webp"
        if os.path.exists(image_address):
            os.remove(image_address)
            print("Image was deleted")
        else:
            print("file not found")
        return redirect("/profile/")

@login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        print(request.POST)
        if form.is_valid():
            print("Password was changed")
            form.save()
        else:
            print("Password was not changed")
            print(form.errors)

        return redirect("/profile/")

@login_required
def add_contact(request):
    user = request.user
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = user
            contact.save()
    return redirect("/profile/")

@login_required
def edit_contact(request, contact_id):
    user = request.user
    if request.method == 'POST':
        instance = models.Contact.objects.get(id = contact_id, user=user)
        if instance:
            form = forms.ContactForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                print("Contact was edited")
            else:
                print("Contact was not edited")
                print(form.errors)
        else:
            print("Contact was not found")
    return redirect("/profile/")

@login_required
def delete_contact(request, contact_id):
    user = request.user
    if request.method == 'GET':
        contact = models.Contact.objects.get(id=contact_id, user=user)
        if contact:
            contact.delete()
            print("Contact deleted")
        else:
            print("Contact not found")
    return redirect("/profile/")


def user_login(request):
    if request.method == 'GET':
        return render(request, "login.html", context={})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print("Error: User not found")
            return redirect('/login/')


def user_signup(request):
    if request.method == 'GET':
        return render(request, "signup.html", context={})
    elif request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            print(form)
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            print("Sign up info is not valid")
            print(form.errors)
            return redirect('/sign-up/')

            
def user_logout(request):
    if request.method == 'GET':
        logout(request)
        return redirect('/login/')