from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime

class NewDataForm(forms.Form):
    def for_edit(self, nam, pric, quant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = nam
        self.fields['price'].initial = pric
        self.fields['quantity'].initial = quant

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'id_name',
            'placeholder': 'Enter product name',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'
        })
    )
    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter product price',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'
        })
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter product quantity',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;'
        })
    )

class CustomerNameForm(forms.Form):
    customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your name',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;',
        })
    )

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    if "names" not in request.session:
        request.session["names"] = []
    if "prices" not in request.session:
        request.session["prices"] = []
    if "quantities" not in request.session:
        request.session["quantities"] = []
    if "quantities_prices" not in request.session:
        request.session["quantities_prices"] = []
    if "total_price" not in request.session:
        request.session["total_price"] = 0
    if "customer_name" not in request.session:
        request.session["customer_name"] = None

    return render(request, 'recipt/index.html', {
        "names": request.session["names"],
        "prices": request.session["prices"],
        "quantities": request.session["quantities"],
        "quantities_prices": request.session["quantities_prices"],
        "total_price": request.session["total_price"],
        "customer_name": request.session["customer_name"],
        'range_5': range(len(request.session["names"])),
        'now': datetime.now()
    })

def add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    if request.method == 'POST':
        form = NewDataForm(request.POST)
        customer_form = CustomerNameForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']

            request.session["names"].append(name)
            request.session["prices"].append(price)
            request.session["quantities"].append(quantity)
            request.session['quantities_prices'].append(price * quantity)
            request.session['total_price'] += price * quantity

            if customer_form.is_valid() and customer_form.cleaned_data['customer_name']:
                request.session['customer_name'] = customer_form.cleaned_data['customer_name']

        else:
            return render(request, 'recipt/add.html', {'form': form, 'customer_form': customer_form})

    return render(request, 'recipt/add.html', {
        "form": NewDataForm(),
        "customer_form": CustomerNameForm() if not request.session["customer_name"] else CustomerNameForm(initial={'customer_name': request.session["customer_name"]})
    })

def new_receipt(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    request.session["names"] = []
    request.session["prices"] = []
    request.session["quantities"] = []
    request.session["quantities_prices"] = []
    request.session["total_price"] = 0
    request.session["customer_name"] = None  # Reset customer name

    return redirect('recipt:add')

def dele(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    try:
        request.session["names"].pop(id)
        request.session["prices"].pop(id)
        request.session["quantities"].pop(id)
        request.session["total_price"] -= request.session["quantities_prices"].pop(id)
    except IndexError:
        pass  # Handle index errors if necessary

    return redirect('recipt:index')

def edit(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    try:
        name = request.session["names"][id]
        price = request.session["prices"][id]
        quantity = request.session["quantities"][id]
    except IndexError:
        return redirect('recipt:index')  # Redirect if index is invalid

    request.session["names"].pop(id)
    request.session["prices"].pop(id)
    request.session["quantities"].pop(id)
    request.session["total_price"] -= request.session["quantities_prices"].pop(id)

    if request.method == 'POST':
        form = NewDataForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']

            request.session["names"].append(name)
            request.session["prices"].append(price)
            request.session["quantities"].append(quantity)
            request.session['quantities_prices'].append(price * quantity)
            request.session['total_price'] += price * quantity

            return redirect('recipt:index')
        else:
            return render(request, 'recipt/add.html', {'form': form})

    else:
        form = NewDataForm()
        form.for_edit(name, price, quantity)
        return render(request, 'recipt/add.html', {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("recipt:index"))
        else:
            return render(request, "recipt/login.html", {
                "message": "Invalid credentials.",
                "username": username  # Retain the entered username
            })
    return render(request, "recipt/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("recipt:login"))
