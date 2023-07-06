from django.urls import path
from .views import *

app_name = 'appointments'

urlpatterns = [

    path('queue', d_queue,  name='d_queue'),
    path('queue/<str:selected_date>/', d_queue, name='d_queue'),

    path('', p_appointments_list,  name='p_appointments'),
    path('referrals', p_referrals_list,  name='p_referrals'),

    path('specialities', p_specialities_list,  name='p_specialities'),
    path('speciality/', p_speciality, name='p_speciality'),
    path('speciality/<int:speciality_id>/', p_speciality, name='p_speciality'),

    path('create_appointment/<int:doctor_id>/',
         p_create_appointment, name='p_create_appointment'),
    path('save_appointment/', p_save_appointment, name='p_save_appointment'),

    path('doctor_available_slots/', doctor_available_slots,
         name='doctor_available_slots'),

    path('confirm_appointment/', d_confirm_appointment,
         name='d_confirm_appointment'),
    path('cancel_appointment/', p_cancel_appointment,
         name='p_cancel_appointment'),

    path('create_referral/', d_create_referral, name='d_create_referral'),







]
