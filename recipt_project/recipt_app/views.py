from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
from .sendmail import viewsdata

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

class CustomerForm(forms.Form):
    def for_edit_customer(self, customer_name, customer_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].initial = customer_name
        self.fields['customer_email'].initial = customer_email

    customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Customer name',
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; margin-bottom: 10px;',
        })
    )
    customer_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
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
    if "customer_email" not in request.session:
        request.session["customer_email"] = None

    return render(request, 'recipt/index.html', {
        "products": request.session["products"],
        "total_price": request.session["total_price"],
        "customer_name": request.session["customer_name"],
        "customer_email": request.session["customer_email"],
        'range_5': range(len(request.session["products"])),
        'now': datetime.now()
    })
def sendmail(request):
    user_data = {
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'products': request.session.get("products"),
        'total_price': request.session.get("total_price"),
        'customer_name': request.session.get("customer_name"),
        'customer_email': request.session.get("customer_email"),
        'now': datetime.now()
    }
    
    result = viewsdata(user_data)

    # Check for delivery error and redirect to edit_customer if email not found
    if result and result.startswith("Error"):
        return redirect('recipt:edit_customer', customer_name=user_data['customer_name'], customer_email=user_data['customer_email'])
    elif result == "Success":
        return render(request, 'recipt/redirect_popup.html', {
            'customer_name': user_data['customer_name']
        })
    else:
        return render(request, 'recipt/redirect_popup.html', {
            'customer_name': user_data['customer_name'],
            'error': 'An unexpected issue occurred while sending the email.'
        })
def add(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))
    
    if request.method == 'POST':
        form = NewDataForm(request.POST)
        form_customer = CustomerForm(request.POST)
        if form.is_valid() and form_customer.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            quantity = form.cleaned_data['quantity']
            quantity_price = price * quantity
            request.session["products"].append([name, quantity, price, quantity_price])
            request.session['total_price'] += quantity_price

            customer_name = form_customer.cleaned_data['customer_name']
            customer_email = form_customer.cleaned_data['customer_email']
            if customer_name:
                request.session["customer_name"] = customer_name
            if customer_email:
                request.session["customer_email"] = customer_email

        else:
            return render(request, 'recipt/add.html', {'form': form, 'form_customer': form_customer})
    return render(request, 'recipt/add.html', {"form": NewDataForm(), 'form_customer': CustomerForm()})

def new_receipt(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    # Reset session data for a new receipt
    request.session["products"] = []
    request.session["total_price"] = 0
    request.session["customer_name"] = None
    request.session["customer_email"] = None
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

def edit_customer(request, customer_name, customer_email):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("recipt:login"))

    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            customer_name = customer_form.cleaned_data['customer_name']
            customer_email = customer_form.cleaned_data['customer_email']
            request.session['customer_name'] = customer_name
            request.session['customer_email'] = customer_email
            return redirect('recipt:index')
    else:
        customer_form = CustomerForm(initial={'customer_name': customer_name, 'customer_email': customer_email})

    return render(request, 'recipt/edit_customer.html', {"customer_form": customer_form, "customer_name": customer_name, "customer_email": customer_email})

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
        form = NewDataForm(initial={'name': name, 'price': price, 'quantity': quantity})

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
