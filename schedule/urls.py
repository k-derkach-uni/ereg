
from django.urls import path
from .views import *

app_name = 'schedule'

urlpatterns = [
    path('', get_schedule, name='schedule'),
    path('<str:date_str>/', get_schedule, name='schedule'),

]
