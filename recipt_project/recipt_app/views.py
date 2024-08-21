from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime

class NewDataForm(forms.Form):
    def for_edit_product(self, nam, pric, quant, *args, **kwargs):
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
    def for_edit_customer(self, customer_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].initial = customer_name

    customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Customer name',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;',
        })
    )

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    if "products" not in request.session:
        request.session["products"] = []  # 2D list to store [name, quantity, price, quantity_price]
    if "total_price" not in request.session:
        request.session["total_price"] = 0
    if "customer_name" not in request.session:
        request.session["customer_name"] = None

    return render(request, 'recipt/index.html', {
        "products": request.session["products"],
        "total_price": request.session["total_price"],
        "customer_name": request.session["customer_name"],
        'range_5': range(len(request.session["products"])),
        'now': datetime.now()
    })

def add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))
    if request.method == 'POST':
        form = NewDataForm(request.POST)
        form_customer = CustomerNameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']
            quantity_price = price * quantity
            request.session["products"].append([name, quantity, price, quantity_price])
            request.session['total_price'] += quantity_price
            if form_customer.is_valid():
                customer_name = form_customer.cleaned_data['customer_name']
                request.session["customer_name"] = customer_name
            # return redirect('recipt:index')  # Redirect after adding
        else:
            return render(request, 'recipt/add.html', {'form': form, 'form_customer': form_customer})
    return render(request, 'recipt/add.html', {"form": NewDataForm(), 'form_customer': CustomerNameForm()})

def new_receipt(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    request.session["products"] = []  # Reset 2D product list
    request.session["total_price"] = 0
    request.session["customer_name"] = None  # Reset customer name

    return redirect('recipt:add')

def dele(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    try:
        product = request.session["products"].pop(id)
        request.session['total_price'] -= product[3]  # Subtract the quantity_price
    except IndexError:
        pass  # Handle index errors if necessary

    return redirect('recipt:index')

def edit_customer(request, customer_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    if not customer_name:
        return redirect('recipt:index')  # Redirect if customer_name is not provided

    if request.method == 'POST':
        customer_form = CustomerNameForm(request.POST)
        if customer_form.is_valid():
            customer_name = customer_form.cleaned_data['customer_name']
            request.session['customer_name'] = customer_name
            return redirect('recipt:index')
        else:
            return render(request, 'recipt/edit_customer.html', {'customer_form': customer_form, 'customer_name': customer_name})
    else:
        customer_form = CustomerNameForm()
        customer_form.for_edit_customer(customer_name)
        return render(request, 'recipt/edit_customer.html', {"customer_form": customer_form, "customer_name": customer_name})

def edit_product(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    try:
        product = request.session["products"][id]
        name, quantity, price, quantity_price = product
    except IndexError:
        return redirect('recipt:index')  # Redirect if invalid ID

    if request.method == 'POST':
        form = NewDataForm(request.POST)
        if form.is_valid():
            # Update session data
            new_name = form.cleaned_data['name']
            new_price = form.cleaned_data['price']
            new_quantity = form.cleaned_data['quantity']
            new_quantity_price = new_price * new_quantity

            # Update the product
            request.session["products"][id] = [new_name, new_quantity, new_price, new_quantity_price]

            # Recalculate total price
            request.session['total_price'] = sum(p[3] for p in request.session["products"])

            return redirect('recipt:index')
    else:
        form = NewDataForm()
        form.for_edit_product(name, price, quantity)

    return render(request, 'recipt/add.html', {"form": form, 'is_editing': True, 'id': id})

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
