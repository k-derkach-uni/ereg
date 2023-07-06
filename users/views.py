from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView

from django.contrib.auth.decorators import login_required
from appointments.models import *
# Create your views here.


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form


def e_reg(request):

    print(request.user.role)

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        else:
            return redirect('/appointments/')
    else:
        return redirect('/login/')


@login_required
def d_patients_list(request):
    if request.user.role != 'DOCTOR':
        # Отправка ошибки 403 Forbidden
        return HttpResponseForbidden("Доступ запрещен")

    search_query = request.GET.get('search', None)

    if search_query:
        # Поиск пациента по ID или ФИО
        patients = Patient.objects.filter(
            Q(id__icontains=search_query) | Q(first_name__icontains=search_query) | Q(
                last_name__icontains=search_query)
        )
    else:
        # Получение последних 10 записей с принятым статусом для текущего врача
        appointments = Appointment.objects.filter(
            doctor=request.user, status='COMPLETED').order_by('-date')[:10]

        # Получение уникальных пациентов из этих записей
        patients = Patient.objects.filter(
            patient_appointments__in=appointments).distinct()

    context = {
        'patients': patients,
        'search_query': search_query,
    }

    return render(request, 'd_patients_list.html', context)
