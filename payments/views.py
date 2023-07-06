from django.http import JsonResponse
import json
from django.http import HttpResponseForbidden
from django.shortcuts import render
from payments.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

# Create your views here.


@login_required
def p_payments_list(request):
    if request.user.role != 'PATIENT':
        # Если роль пользователя не "PATIENT", возвращаем ответ с ошибкой 403 Forbidden
        return HttpResponseForbidden('Доступ запрещен.')

    # Предполагается, что связь с пациентом настроена в модели пользователя
    patient = request.user
    # Получаем оплаты, связанные с пациентом
    payments = Invoice.objects.filter(patient=patient)

    context = {
        'payments_list': payments
    }
    return render(request, 'p_payments_list.html', context)


@login_required
def payment_detail(request, invoice_id):
    payment = get_object_or_404(Invoice, id=invoice_id)
    context = {
        'payment': payment,
    }

    if request.user.role == 'PATIENT':
        context['template'] = 'patient_base.html'
    elif request.user.role == 'DOCTOR':
        context['template'] = 'doctor_base.html'
    else:
        context['template'] = 'base.html'  # Шаблон по умолчанию
    return render(request, 'payment_detail.html', context)


@login_required
def d_create_invoice(request):
    if request.user.role != 'DOCTOR':
        # Если пользователь не является врачом, возвращаем ошибку доступа
        return JsonResponse({'success': False, 'message': 'Доступ запрещен.'})

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        # Получение данных из запроса
        service_data = data['services']
        patient_id = data['patient_id']

        # Проверка наличия пациента
        if not patient_id:
            return JsonResponse({'success': False, 'message': 'Не указан пациент.'})

        # Создание счета
        invoice = Invoice.objects.create(
            doctor=request.user, patient_id=patient_id)

        # Добавление выбранных услуг в счет
        for service in service_data:
            service_name = service.get('service')
            quantity = service.get('quantity')
            price = service.get('price')
            service_id = service.get('id')

            # Проверка наличия необходимых данных
            if not service_name or not quantity or not price or not service_id:
                continue

            # Замена запятой на точку в цене
            price = price.replace(',', '.')

            # Рассчитываем общую стоимость услуги
            total_price = float(price) * int(quantity)

            # Создаем связь между счетом и услугой
            invoice_service = InvoiceService.objects.create(
                invoice=invoice,
                service_id=service_id,
                quantity=quantity,
                total_price=total_price
            )
        total_amount = 0
        for invoice_service in invoice.invoiceservice_set.all():
            total_amount += invoice_service.total_price

        invoice.total_amount = total_amount
        invoice.save()

        # Возвращаем успешный результат и данные счета в JSON-формате
        return JsonResponse({'success': True, 'message': 'Счет успешно создан.', 'invoice_id': invoice.id})

    # Если запрос не является POST-запросом, возвращаем ошибку
    return JsonResponse({'success': False, 'message': 'Недопустимый запрос.'})
