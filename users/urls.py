from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('ereg/', e_reg,  name='e_reg'),
    path('patients/', d_patients_list,  name='d_patients_list'),

]
