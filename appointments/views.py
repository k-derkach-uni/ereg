from datetime import date, datetime
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from users.models import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from payments.models import *


def doctor_available_slots(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        doctor_id = request.GET.get('doctor_id')
        doctor = Doctor.objects.get(id=doctor_id)

        # Преобразование строки даты в объект datetime.date
        date = datetime.strptime(date_str, '%d.%m.%Y').date()

        slots = doctor.get_available_slots(date)
        # Преобразование слотов в формат "hh:mm"
        slot_times = [slot.strftime('%H:%M') for slot in slots]
        return JsonResponse(slot_times, safe=False)

    return JsonResponse([], safe=False)


@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def p_appointments_list(request):
    if request.user.role == 'PATIENT':
        appointments = Appointment.objects.filter(
            patient=request.user).order_by('-id')
        template = 'p_appointments_list.html'

    else:
        return HttpResponseForbidden()

    context = {
        'appointments_list': appointments,
    }

    return render(request, template, context)


def p_specialities_list(request):
    specialties = Speciality.objects.filter(
        doctorproperties__visible=True).distinct()
    context = {'specialties': specialties}
    return render(request, 'p_specialties_list.html', context)


def p_speciality(request, speciality_id=None):
    referral_id = request.GET.get('referral_id')
    if referral_id and referral_id != 'None':
        referral_id = int(referral_id)
        referral = Referral.objects.get(id=referral_id)
        speciality = referral.speciality
        doctors = Doctor.objects.filter(
            doctorproperties__speciality=speciality)
        speciality_id = speciality.id
    else:
        speciality = Speciality.objects.get(id=speciality_id)
        doctors = Doctor.objects.filter(
            doctorproperties__speciality=speciality, doctorproperties__visible=True)

    selected_date = request.GET.get('selected_date')
    today = date.today()
    if selected_date and selected_date >= str(today):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        available_doctors = []
        for doctor in doctors:
            if doctor.get_available_slots(selected_date):
                available_doctors.append(doctor)
        doctors = available_doctors

    context = {'referral_id': referral_id, 'speciality': speciality,
               'doctors': doctors, 'selected_date': selected_date}
    return render(request, 'p_speciality.html', context)


def p_create_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    referral_id = request.GET.get('referral_id')
    referral = None

    if referral_id and referral_id != 'None':
        referral_id = int(referral_id)
        referral = get_object_or_404(Referral, id=referral_id)
        if referral.patient != request.user:
            return HttpResponseForbidden('Нет доступа к данному направлению.')

    selected_date = request.GET.get('selected_date')
    today = date.today()
    if selected_date and selected_date >= str(today):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        available_slots = doctor.get_available_slots(selected_date)
    else:
        available_slots = []

    context = {
        'doctor': doctor,
        'selected_date': selected_date,
        'available_slots': available_slots,
        'referral_id': referral_id,
    }

    return render(request, 'p_create_appointment.html', context)


def p_save_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        selected_date = request.POST.get('selected_date')
        slot = request.POST.get('slot')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        referral_id = request.POST.get('referral_id')
        referral = None

        if referral_id and referral_id != 'None':
            referral_id = int(referral_id)

            referral = get_object_or_404(Referral, id=referral_id)
            if referral.patient != request.user:
                return JsonResponse({'success': False, 'message': 'Нет доступа к данному направлению.'})

        # Проверка на существующую активную запись
        existing_appointment = Appointment.objects.filter(
            doctor=doctor, patient=request.user, status=Appointment.Status.WAITING).exists()
        if existing_appointment:
            return JsonResponse({'success': False, 'message': 'У вас уже есть активная запись на прием к этому врачу.'})

        # Проверка на наличие свободного слота
        available_slots = doctor.get_available_slots(selected_date)
        slot_time = datetime.strptime(slot, "%H:%M").time()
        slot_available = slot_time in available_slots
        if not slot_available:
            return JsonResponse({'success': False, 'message': 'Выбранный слот недоступен. Пожалуйста, выберите другой слот.'})

        # Создание новой записи на прием
        appointment = Appointment(doctor=doctor, patient=request.user,
                                  date=selected_date, time=slot_time, status=Appointment.Status.WAITING)
        appointment.save()

        if referral:
            referral.appointment = appointment
            referral.save()

        return JsonResponse({'success': True, 'message': 'Запись на прием успешно создана.'})


@login_required
def d_queue(request, selected_date=None):
    if request.user.role != 'DOCTOR':
        # Отправка ошибки 403 Forbidden
        return HttpResponseForbidden("Доступ запрещен")

    if selected_date:
        selected_date = timezone.datetime.strptime(
            selected_date, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    appointments = Appointment.objects.filter(
        Q(doctor=request.user) & Q(date=selected_date) & (
            Q(status='WAITING') | Q(status='COMPLETED'))
    ).order_by('time')
    # Количество пациентов в очереди со статусом WAITING
    waiting_count = appointments.filter(
        status=Appointment.Status.WAITING).count()

    # Формирование ссылок на прошлый и следующий день
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    # Проверка, является ли выбранная дата сегодняшней
    is_today = selected_date == timezone.now().date()

    # Получение дат выходных дней для текущего и следующего месяца
    current_month = selected_date.month
    next_month = current_month + 1 if current_month < 12 else 1
    current_year = selected_date.year
    next_year = current_year if next_month > 1 else current_year + 1

    dayoffs = []
    doctor = Doctor.objects.get(id=request.user.id)
    for day in range(1, 32):  # Проверяем все числа от 1 до 31
        try:
            check_date = date(current_year, current_month, day)
        except ValueError:
            # Пропускаем, если дата недопустима (например, 30 февраля)
            continue

        start_time, end_time = doctor.get_schedule_for_date(check_date)
        if start_time is None and end_time is None:
            dayoffs.append(check_date)

    for day in range(1, 32):  # Проверяем все числа от 1 до 31
        try:
            check_date = date(next_year, next_month, day)
        except ValueError:
            # Пропускаем, если дата недопустима (например, 30 февраля)
            continue

        start_time, end_time = doctor.get_schedule_for_date(check_date)
        if start_time is None and end_time is None:
            dayoffs.append(check_date)
    context = {
        'appointments_list': appointments,
        'selected_date': selected_date,
        'waiting_count': waiting_count,
        'prev_date': prev_date,
        'next_date': next_date,
        'is_today': is_today,
        'dayoffs': dayoffs,
        'specialities': Speciality.objects.all().order_by('name'),
        'services': Service.objects.filter(speciality=doctor.doctorproperties.speciality).order_by('name')
    }

    return render(request, 'd_queue.html', context)


@login_required
def d_confirm_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')

        # Получаем объект записи по идентификатору
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Проверяем, что текущий пользователь является врачом записи
        if appointment.doctor != request.user:
            return JsonResponse({'success': False, 'message': 'У вас нет прав для подтверждения этого приема'})

        appointment.status = 'COMPLETED'
        appointment.save()

        # Возвращаем ответ клиенту
        return JsonResponse({'success': True, 'message': 'Прием подтвержден'})
    return JsonResponse({'success': False, 'message': 'Ошибка'})


@login_required
def p_cancel_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        # Получение объекта записи или возврат ошибки 404, если запись не найдена
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Проверка, является ли текущий пользователь пациентом записи
        if appointment.patient != request.user:
            return JsonResponse({'success': False, 'message': 'Вы не можете отменить эту запись.'})

        # Изменение статуса на 'PATIENT_CANCELLED'
        appointment.status = Appointment.Status.PATIENT_CANCELLED
        appointment.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'})


@login_required
def d_create_referral(request):
    patient_id = request.POST.get('patient_id')
    speciality = request.POST.get('speciality')
    diagnosis = request.POST.get('diagnosis')
    purpose = request.POST.get('purpose')

    referral = Referral.objects.create(
        patient=Patient.objects.get(id=patient_id),
        referring_doctor=request.user,
        speciality=Speciality.objects.get(id=speciality),
        diagnosis=diagnosis,
        purpose=purpose
    )
    referral.save()
    return JsonResponse({'success': True})


@login_required
def p_referrals_list(request):
    # Проверка роли пользователя
    if request.user.role != 'PATIENT':
        return HttpResponseForbidden("Access denied")

    # Получение направлений пациента
    referrals = Referral.objects.filter(patient=request.user)

    context = {
        'referrals': referrals
    }

    return render(request, 'p_referrals_list.html', context)
