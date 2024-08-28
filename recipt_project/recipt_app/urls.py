from django.urls import path
from . import views

app_name = 'recipt'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('new/', views.new_receipt, name='new_receipt'),
    path('delete/<int:id>/', views.dele, name='dele'),
    path('edit_product/<int:id>/', views.edit_product, name='edit_product'),
    path('edit_customer/<str:customer_name>/<str:customer_email>/', views.edit_customer, name='edit_customer'),
    path('sendmail/', views.sendmail, name='sendmail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
