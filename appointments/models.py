from django.db import models
from users.models import *
# Create your models here.
from django.utils import timezone


class Appointment(models.Model):

    class Status(models.TextChoices):
        WAITING = 'WAITING', 'В очереди'
        COMPLETED = 'COMPLETED', 'Принят'
        MISSED = 'MISSED', 'Пропущен'
        CANCELLED = 'CANCELLED', 'Отменен'
        PATIENT_CANCELLED = 'PATIENT_CANCELLED', 'Отменен пациентом'

    patient = models.ForeignKey(Patient, verbose_name='Пациент',
                                on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, verbose_name='Врач',
                               on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField('Дата приема')
    time = models.TimeField('Время приема')
    status = models.CharField(
        'Статус приема', max_length=50, choices=Status.choices)

    @property
    def get_status(self):
        return self.get_status_display()

    class Meta:
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'

    def save(self, *args, **kwargs):
        if not self.status:
            self.status = 'WAITING'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.date}'


class Referral(models.Model):
    referring_doctor = models.ForeignKey(
        Doctor, verbose_name='Врач, направивший', on_delete=models.CASCADE)

    patient = models.ForeignKey(Patient, verbose_name='Пациент',
                                on_delete=models.CASCADE, related_name='patient_refs', null=True)
    speciality = models.ForeignKey(
        Speciality, verbose_name='Специальность', on_delete=models.CASCADE, null=True)

    date_added = models.DateField('Дата добавления', default=timezone.now)
    diagnosis = models.CharField(
        'Диагноз', max_length=100, null=True, blank=True)
    purpose = models.CharField('Назначение', max_length=100)
    appointment = models.OneToOneField(Appointment, verbose_name='Запись на прием',
                                       null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Направление от {self.referring_doctor} ({self.date_added})"
