from django.urls import path
from . import views

app_name = 'recipt'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('new/', views.new_receipt, name='new_receipt'),
    path('delete/<int:id>/', views.dele, name='dele'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
