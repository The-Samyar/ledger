from django.shortcuts import render, redirect
from django.contrib.auth import models, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from . import models, forms
from .models import User_info, Transaction
import json
import datetime
from django.core import serializers
from django.contrib.auth.forms import PasswordChangeForm
from PIL import Image
from pathlib import Path
import os



user = models.User.objects.get(username="akbar")

# TODO generate colors on demand
BALANCE_BANK_COLORS = ["rgb(133, 105, 241)",
                       "rgb(164, 101, 241)",
                       "rgb(101, 143, 241)",
                       "rgb(208, 46, 203)",
                       "rgb(226, 141, 181)",
                       "rgb(71, 92, 230)",
                        ]

MONTHS = ["January","February","March","April","May","June","July","August","September", "October", "November", "December"]

# Create your views here.
# def index(request):
#     context = {
#         # 'card' : user.card_set.all(),
#         # 'card' : user.cards.first(),
#         'user' : user,
#     }
#     return render(request, "index.html", context)

def index(request):
    # TODO filter 'incomes' and 'expenses' to show only for the current month

    user_cards = user.cards.all()
    transactions = models.Transaction.objects.filter(card__in=user_cards).order_by('-date_time')
    deposits = transactions.filter(action='deposit')
    withdraws = transactions.filter(action='withdraw')

    doughnutChartData = {
        "labels": list(user_cards.values_list('bank_name',flat=True)),
        "datasets" : [{
                "label": "Balance",
                "data": list(user_cards.values_list('balance',flat=True)),
                "backgroundColor": BALANCE_BANK_COLORS[:len(user_cards)],
                "hoverOffset": 20,
                },],
    }
    doughnutChartData = json.dumps(doughnutChartData)

    now = datetime.datetime.now()
    labels = []
    total_withdraws = []
    total_deposits = []
    for i in range(6):
        desired_month = ((now.month-1) + 7 + i) % 12
        labels.append(MONTHS[desired_month])
        a = withdraws.filter(date_time__year=now.year, date_time__month=desired_month+1).aggregate(total=Sum('amount'))['total']
        b = deposits.filter(date_time__year=now.year, date_time__month=desired_month+1).aggregate(total=Sum('amount'))['total']
        total_withdraws.append(a if a != None else 0)
        total_deposits.append(b if b != None else 0)

    

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
        # const labels = ["January", "February", "March", "April", "May", "June"];
        # const data = {
        #     labels: labels,
        #     datasets: [
        #     {
        #         label: "My First dataset",
        #         backgroundColor: "hsl(217, 57%, 51%)",
        #         borderColor: "hsl(217, 57%, 51%)",
        #         data: [0, 10, 5, 2, 20, 30, 45],
        #     },
        #     ],
        # };

    lineChartData = json.dumps(lineChartData)

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
    }

    return render(request, "index.html", context)

def transactions(request):
    if request.method == 'GET':
        context = {
            'user' : user,
            'transactions' : models.Transaction.objects.filter(card__in=user.cards.all()).order_by('-date_time')
        }
        return render(request, "transactions.html", context)
    elif request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            user_card = form.cleaned_data['card']
            if form.cleaned_data['action'] == 'deposit':
                user_card.balance += form.cleaned_data['amount']
            else:
                user_card.balance -= form.cleaned_data['amount']
            user_card.save(), form.save()
            print("SUCCESS")
        else:
            print("FAIL")
            print(form.errors)
        return redirect('/transactions/')

    

def edit_transaction(request, transaction_id):
    if request.method == 'POST':
        form = forms.TransactionForm(
            request.POST,
            instance = models.Transaction.objects.get(_transaction_id=transaction_id)
            )
        if form.is_valid() == True:
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
            print("SUCCESS")
        else:
            print(form.errors.as_json)
        return redirect('/transactions/')
    
def delete_transaction(request, transaction_id):
    target_transaction = models.Transaction.objects.get(_transaction_id=transaction_id)
    if target_transaction:
        user_card = target_transaction.card
        if target_transaction.action == 'deposit':
            user_card.balance -= target_transaction.amount
        else:
            user_card.balance += target_transaction.amount

        target_transaction.delete(), user_card.save()
        print("SUCCESS")
    else:
        print("FAIL")
    return redirect('/transactions/')

def cards(request):
    if request.method == 'GET':
        today = datetime.datetime.now()
        user_cards = user.cards.all()
        date_format = "%m %d"
        current_balance = user_cards.aggregate(total_balance=Sum('balance'))['total_balance']
        labels = [today.strftime(date_format)]
        # daily_balance = [current_balance]
        user_transactions = models.Transaction.objects.filter(card__in=user_cards)
        datasets = [{
                    "label": "Total balance",
                    "backgroundColor": "hsl(0, 0%, 100%)",
                    "borderColor": "hsl(0, 0%, 100%)",
                    "data": [current_balance],
                    },
                    ]
        for k in range(len(user_cards)):
            datasets.append({
                "label": user_cards[k].bank_name,
                "backgroundColor": BALANCE_BANK_COLORS[k],
                "borderColor": BALANCE_BANK_COLORS[k],
                "data": [user_cards[k].balance,],
                })

        for i in range(1,30):
            target_date = today - datetime.timedelta(days=i)
            # day_after = target_date + datetime.timedelta(days=1)
            labels.append(target_date.strftime(date_format))
            # target_date = today - datetime.timedelta(days=i)
            target_date = target_date + datetime.timedelta(days=1)
            daily_transactions = user_transactions.filter(date_time__year=target_date.year, date_time__month=target_date.month,date_time__day=target_date.day)
            total_balance = 0
            for j in range(1,len(datasets)):
                transactions_sums = daily_transactions.aggregate(
                    deposits_sum=Sum('amount', filter=(Q(action='deposit') & Q(card=user_cards.get(bank_name=datasets[j]['label']))), default=0),
                    withdraws_sum=Sum('amount', filter=(Q(action='withdraw') & Q(card=user_cards.get(bank_name=datasets[j]['label']))), default=0)
                    )
                # print(transactions_sums)
                # deposits_sum = daily_transactions.filter(
                #     card=user_cards.get(bank_name=datasets["label"])
                #     ).aggregate(
                #     deposits_sum=Sum('amount', default=0)
                #     )["deposits_sum"]
                # withdraws_sum = daily_transactions.filter(
                #     card=user_cards.get(bank_name=datasets["label"])
                #     ).aggregate(
                #     withdraws_sum=Sum('amount', default=0)
                #     )["withdraws_sum"]
                card_balance = datasets[j]['data'][-1] - transactions_sums['deposits_sum'] + transactions_sums['withdraws_sum']
                # print(card_balance)
                datasets[j]['data'].append(card_balance)
                total_balance += card_balance
            datasets[0]["data"].append(total_balance)

            # print(datasets)
        # labels.reverse(), daily_balance.reverse()

        # for i, j in zip(labels, daily_balance):
        #     print(f"{i}---{j}")
        for dataset in datasets:
            dataset["data"].reverse()
        labels.reverse()
        
        lineChartData = {
            "labels": labels,
            "datasets" : datasets,
        }

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
        form = forms.CardForm(request.POST)
        if form.is_valid():
            new_card = form.save(commit=False)
            new_card.user = user
            new_card.save()
            print("CARD SUCCESSFULLY ADDED ")
        else:
            print("FAIL")
            print("Errors:")
            print(request.POST)
            print(form.errors)

        return redirect('/cards/')
    
def edit_card(request, card_id):
    if request.method == 'POST':
        form = forms.CardForm(request.POST, instance=models.Card.objects.get(user=user, id=card_id))
        print(form)
        if form.is_valid():
            form.save()
            print("EDIT SUCCESS")
            print(form.fields)
        else:
            print("EDIT FAILED")
            print("Errors:")
            print(form.errors)

        return redirect('/cards/')

def delete_card(request, card_id):
    if request.method == 'GET':
        card = models.Card.objects.get(user=user, id=card_id)
        if card:
            print("CARD DELETE SUCCESS")
            card.delete()
        else:
            print("CARD DELETE FAIL")
            print("CARD NOT FOUND")
        return redirect('/cards/')
    
def profile(request):
    if request.method == 'GET':
        context = {
            'user_info' : user,
            'user_contacts': user.contacts.all(),
            'genders' : models.User_info.gender.field.choices,
        }
        return render(request, 'profile.html', context=context)
    elif request.method == 'POST':
        user_form = forms.UserForm(request.POST, instance=user)
        user_info_form = forms.User_infoForm(request.POST, instance=user.extra_info)
        print(user_info_form)
        if user_form.is_valid():
            if user_info_form.is_valid():
                print("####################")
                print("BOTH FORMS ARE VALID")
                print(request.POST)
                print(user_info_form.cleaned_data)
                
                user_form.save()
                user_info_form.save()
                print(user.extra_info.gender)
                print("Saved")
                return redirect("/profile/")
            else:
                print("####################")
                print("PROBLEM IN FORM2")
                print(user_info_form.errors)
                return redirect("/profile/")
        else:
            print("####################")
            print("PROBLEM IN FORM1")
            return redirect("/profile/")

def add_pic(request):
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

def delete_pic(request):
    if request.method == 'GET':
        image_address = f"main/static/main/img/users/{user.username}/profile.webp"
        if os.path.exists(image_address):
            os.remove(image_address)
            print("deleted")
        else:
            print("file not found")
            print(image_address)
        return redirect("/profile/")

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        print(request.POST)
        if form.is_valid():
            print("##################")
            print("Password change is valid")
            form.save()
        else:
            print("##################")
            print("There is an issue with password change:")
            print(form.errors)

        return redirect("/profile/")

def add_contact(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = user
            contact.save()
    return redirect("/profile/")

def edit_contact(request, contact_id):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST, instance=models.Contact.objects.get(id = contact_id))
        print(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            print("Contact edited")
        else:
            print("There was some problem with editing your contact")
            print(form.errors)
    return redirect("/profile/")

def delete_contact(request, contact_id):
    if request.method == 'GET':
        contact = models.Contact.objects.get(id=contact_id, user=user)
        if contact:
            contact.delete()
            print("Contact deleted")
        else:
            print("Contact not found")
    return redirect("/profile/")

def login(request):
    if request.method == 'GET':
        return render(request, "login.html", context={})
    elif request.method == 'POST':
        return redirect('/')

def signup(request):
    if request.method == 'GET':
        return render(request, "signup.html", context={})
    elif request.method == 'POST':
        return redirect('/')

def logout(request):
    if request.method == 'GET':
        return redirect('/')

'''
def LoginPage(request):

    if request.method == 'GET':
        context = {}
        return render(request, 'login.html', context)

    elif request.method == 'POST':
        next = request.POST['next']
        if not next:
            next = 'api:home'

        username = request.POST['username']
        password = request.POST['password']
                
        user = authenticate(request, username=username, password=password)

        if user is None:
            context = {}
            return render(request, 'login.html', context)
        
        elif user is not None:
            login(request, user)
            return redirect(next)


def SignupPage(request):
    if request.method == 'GET':

        form = UserCreationForm()

        context = {'form' : form}
        return render(request, 'signup.html', context)

    elif request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            username = request.POST['username']
            password = request.POST['password1']
                    
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('api:home')
        else:
            print('form not valid')
    else:
        print('error')

@login_required       
def Homepage(request):

    # Finds all the cards for the user and reformats them into a list

    # Solution #1
    # user_cards = []
    # temp = Cards.objects.filter(user_id=request.user.id)
    # for i in range(len(temp)):
    #     user_cards.append(temp[i].card_number)


    # Solution #2 -- Same output but simpler and lesser code

    user_cards = Card.objects.filter(user_id=request.user.id).values_list('card_number')
    income = Transaction.objects.filter(card_number__in = user_cards, action = 'deposit').aggregate(Sum('amount'))
    expenses = Transaction.objects.filter(card_number__in = user_cards, action = 'withdraw').aggregate(Sum('amount'))
    balance = (income['amount__sum'] - expenses['amount__sum'])
    data = Transaction.objects.filter(card_number__in = user_cards)
    
    context = { 'date' : datetime.utcnow().strftime('%Y, %m, %d'),
                'username' : request.user,
                'balance' : balance,
                'income' : income,
                'expenses' : expenses,
                'data' : data
                }
    return render(request, 'homepage.html', context)

@login_required
def Homepage_redirect(request):
    return redirect(reverse('api:home'))


@login_required
def addTransaction(request):

    if request.method == 'GET':
        context = {'form' : NewTransaction(request)}
        return render(request, 'addTransaction.html', context)

    elif request.method == 'POST':

        form = NewTransaction(request, request.POST)

        if form.is_valid():

            transaction = form.save(commit=False)

            # now stores the time at the moment in Universal Standard Time (UTC)
            # card_number stores the card number used at the time of purchase
            # now and card_number combined with username of the user produce a unique 
            # transaction id per transaction. (now/username/last for digits of card_number) 

            now = datetime.utcnow().strftime('%y%m%d%H%M%S')
            card_number = str(form.cleaned_data['card_number'])
            transaction_id = now + str(request.user) + card_number[-4:]

            transaction.transaction_id = transaction_id
            transaction.save()

        else :
            print('#################\n#################\nERROR\n#################\n#################') 


        return redirect('api:home')

@login_required
def addCard(request):

    if request.method == 'GET':
        context = {'form' : NewCard()}
        return render(request, 'addCard.html', context)

    elif request.method == 'POST':
        form = NewCard(request.POST)

        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
        
        return redirect('api:home')

def Logout(request):
    logout(request)
    return redirect('api:login')

'''