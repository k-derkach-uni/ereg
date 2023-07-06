from django.urls import path
from .views import *

app_name = 'payments'

urlpatterns = [

    path('', p_payments_list, name='p_payments'),
    path('<int:invoice_id>/', payment_detail, name='payment_detail'),
    path('create_invoice/', d_create_invoice, name='d_create_invoice'),


]
