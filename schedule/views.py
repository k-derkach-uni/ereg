from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.http import JsonResponse
from datetime import timedelta
from users.models import *
from django.urls import reverse
from .models import ScheduleException
from .models import *


def get_schedule(request, date_str=None):
    if request.method == "POST":

        doctor_id = request.POST.get('doctor_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        doctor = Doctor.objects.get(id=doctor_id)
        if len(start_time) > 0:
            exception = ScheduleException(
                doctor=doctor, start_date=start_date, end_date=end_date, start_time=start_time, end_time=end_time)
        else:
            exception = ScheduleException(
                doctor=doctor, start_date=start_date, end_date=end_date)

        exception.save()

        return JsonResponse({'status': 'ok'})

    # Вычисляем начальную дату
    if date_str:
        date = datetime.strptime(date_str, '%d-%m-%Y').date()
    else:
        date = datetime.today().date()
    # Начинаем с понедельника текущей недели
    date = date - timedelta(days=date.weekday())

    # Добавляем ссылки на даты через 7 дней и 7 дней назад
    prev_week = (date - timedelta(days=7)).strftime('%d-%m-%Y')
    next_week = (date + timedelta(days=7)).strftime('%d-%m-%Y')
    context = {
        'prev_week_url': reverse('schedule:schedule', args=[prev_week]),
        'next_week_url': reverse('schedule:schedule', args=[next_week]),
    }
    current_week = (date - timedelta(days=date.weekday())) == (
        datetime.today().date() - timedelta(days=datetime.today().date().weekday()))
    if current_week:
        context['prev_week_url'] = None

    # Берем всех врачей, если пользователь является админом, иначе только видимых врачей
    if request.user.is_staff:
        doctors = Doctor.objects.all()
    else:
        doctors = Doctor.objects.filter(doctorproperties__visible=True)

    date_list = [date + timedelta(days=i) for i in range(7)]

    # Получаем расписание каждого врача и сохраняем в контекст
    s = {}
    for doctor in doctors:
        schedules = []
        for d in date_list:
            schedule = doctor.get_schedule_for_date_str(d)
            schedules.append(schedule)
        s[doctor.id] = schedules

    context['schedules'] = s
    context['date_list'] = date_list
    context['doctors'] = doctors
    context['range'] = range(7)

    if request.user.is_staff:
        context['template'] = 'admin/base.html'
    elif request.user.role == 'PATIENT':
        context['template'] = 'patient_base.html'
    elif request.user.role == 'DOCTOR':
        context['template'] = 'doctor_base.html'
    else:
        return redirect('login')

    return render(request, 'schedule.html', context)
