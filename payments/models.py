from django.db import models
from users.models import Doctor, Patient
from django.utils import timezone
# Create your models here.


class Invoice(models.Model):
    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'

    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Оплачено'
        WAITING = 'WAITING', 'Не оплачено!'

    SEX_CHOICES = [
        (1, 'Мужчина'),
        (0, 'Женщина')
    ]

    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                related_name='patient_invoices', verbose_name='Пациент')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE,
                               related_name='doctor_invoices', verbose_name='Врач-исполнитель')
    services = models.ManyToManyField(
        'Service', through='InvoiceService', verbose_name='Услуги')
    payment_date = models.DateTimeField('Дата оплаты', null=True, blank=True)
    total_amount = models.DecimalField(
        'Сумма', max_digits=8, decimal_places=2, default=0)
    status = models.CharField('Статус', max_length=100,
                              choices=Status.choices, default=Status.WAITING)

    @property
    def get_status(self):
        return self.get_status_display()

    def __str__(self) -> str:
        formatted_date = self.creation_date.strftime('%d.%m.%Y')
        return f'Счет пациента id{self.patient.id} от {formatted_date}'

    def save(self, *args, **kwargs):
        if self.status == 'CONFIRMED' and not self.payment_date:
            self.payment_date = timezone.now()
        elif self.status != 'CONFIRMED':
            self.payment_date = None
        super().save(*args, **kwargs)


class Service(models.Model):
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Оказываемые услуги'

    name = models.CharField('Наименование', max_length=100)
    price = models.DecimalField('Цена (р.)', max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price}"


class InvoiceService(models.Model):
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Оказанные услуги'
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, verbose_name='Услуга')
    quantity = models.PositiveIntegerField('Количество', default=1)
    total_price = models.DecimalField(
        'Цена (р.)', max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.service.name
