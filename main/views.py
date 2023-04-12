from django.shortcuts import render
from django.contrib.auth import models
from django.db.models import Sum
from . import models
import json
from datetime import datetime

user = models.User.objects.get(username="akbar")

# TODO generate colors on demand
BALANCE_BANK_COLORS = ["rgb(133, 105, 241)",
                       "rgb(164, 101, 241)",
                       "rgb(101, 143, 241)",
                       "rgb(46, 23, 96)",
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
                "hoverOffset": 10,
                },],
    }
    doughnutChartData = json.dumps(doughnutChartData)

    now = datetime.now()
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
    # print(transactions.filter(action='deposit'))
    # print(transactions.filter(action='withdraw'))
    return render(request, "index.html", context)

def transactions(request):
    context = {
        'user' : user,
        'transactions' : models.Transaction.objects.filter(card__in=user.cards.all())
    }
    return render(request, "transactions.html", context)
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