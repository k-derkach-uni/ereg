from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from users.models import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Schedule(models.Model):
    name = models.CharField('Наименование', max_length=150,
                            help_text='Напр. август, 1-я смена', default='Расписание')
    doctors = models.ManyToManyField(
        Doctor, verbose_name='Медработники', related_name='schedules')
    start_date = models.DateField('Период с')
    end_date = models.DateField('Период до')
    monday_start = models.TimeField('Начало', null=True, blank=True)
    monday_end = models.TimeField('Конец', null=True, blank=True)
    tuesday_start = models.TimeField('Начало', null=True, blank=True)
    tuesday_end = models.TimeField('Конец', null=True, blank=True)
    wednesday_start = models.TimeField('Начало', null=True, blank=True)
    wednesday_end = models.TimeField('Конец', null=True, blank=True)
    thursday_start = models.TimeField('Начало', null=True, blank=True)
    thursday_end = models.TimeField('Конец', null=True, blank=True)
    friday_start = models.TimeField('Начало', null=True, blank=True)
    friday_end = models.TimeField('Конец', null=True, blank=True)
    saturday_start = models.TimeField('Начало', null=True, blank=True)
    saturday_end = models.TimeField('Конец', null=True, blank=True)
    sunday_start = models.TimeField('Начало', null=True, blank=True)
    sunday_end = models.TimeField('Конец', null=True, blank=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'

    def __str__(self):
        return self.name


class ScheduleException(models.Model):
    doctor = models.ForeignKey(
        Doctor, verbose_name='Врач', on_delete=models.CASCADE)
    start_date = models.DateField('Период с')
    end_date = models.DateField('Период до')
    start_time = models.TimeField(
        'Начало', null=True, blank=True, help_text='Оставьте пустым для пропуска')
    end_time = models.TimeField('Конец', null=True, blank=True)

    class Meta:
        verbose_name = 'Изменение в расписании '
        verbose_name_plural = 'Изменения в расписании (исключения)'

    def __str__(self):
        start_date_str = self.start_date.strftime('%d.%m.%Y')
        end_date_str = self.end_date.strftime('%d.%m.%Y')
        return f'{start_date_str}-{end_date_str}, {self.doctor}'

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(
                    _('Start date cannot be later than end date.'))
            if self.start_date == self.end_date and self.start_time >= self.end_time:
                raise ValidationError(
                    _('Start time cannot be later than or equal to end time for the same day.'))

        if self.start_date == datetime.today().date() and self.start_time <= datetime.now().time():
            raise ValidationError(
                _('Start time cannot be earlier than current time.'))

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError(
                "Время начала не может быть больше времени окончания")

        if self.pk is None:  # объект еще не сохранен, создаем новую запись
            # Удаляем все записи с таким же диапазоном дат
            ScheduleException.objects.filter(
                doctor=self.doctor,
                start_date=self.start_date,
                end_date=self.end_date
            ).delete()

        super().save(*args, **kwargs)
