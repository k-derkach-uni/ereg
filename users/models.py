from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from datetime import date, datetime, timedelta, time
from django.db.models import Q
from django.contrib.auth.models import Group
# from django.contrib.auth.hashers import make_password
from ereg.utils import generate_password_and_notify
from PIL import Image


class User(AbstractUser):
    # def set_password(self, raw_password):
    #    self.password = make_password(raw_password)
    username = models.EmailField(
        'Эл. почта', unique=True, validators=[validate_email])

    class Role(models.TextChoices):
        DOCTOR = 'DOCTOR', 'Медработник'
        PATIENT = 'PATIENT', 'Пациент'
        REGISTRAR = 'REGISTRAR', 'Регистратор'

    SEX_CHOICES = [
        (1, 'Мужчина'),
        (0, 'Женщина')
    ]

    role = models.CharField('Роль', max_length=50, choices=Role.choices)

    last_name = models.CharField('Фамилия', max_length=50)
    first_name = models.CharField('Имя', max_length=50)
    patronymic = models.CharField('Отчество', max_length=50)
    sex = models.BooleanField('Пол', choices=SEX_CHOICES, default=1)
    birth_date = models.DateField('Дата рождения', default='1970-01-01')
    phone_number = models.CharField(
        'Номер телефона', max_length=12, default='-')

    @property
    def age(self):
        today = date.today()
        age = today.year - self.birth_date.year
        if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
            age -= 1
        return age

    @property
    def get_short_name(self):
        return f'{self.last_name} {self.first_name[0]}. {self.patronymic[0]}.'

    def __str__(self):
        return f'({self.username}) {self.last_name} {self.first_name} {self.patronymic}'

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'

    def save(self, *args, **kwargs):
        if not self.pk:
            # Если объект не сохранен в базе данных, то создаем пароль
            password = generate_password_and_notify(self.username)
            self.set_password(password)

        super().save(*args, **kwargs)


class Speciality(models.Model):
    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'
    name = models.CharField('Наименование специальности', max_length=150)
    interval = models.IntegerField(
        'Длительность одного приема (мин.)', default=20)
    services = models.ManyToManyField(
        'payments.Service', verbose_name='Оказываемые услуги')

    def __str__(self) -> str:
        return self.name

#   registrar REGISTRAR


class RegistrarManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.REGISTRAR)


class Registrar(User):
    objects = RegistrarManager()

    class Meta:
        proxy = True
        verbose_name = 'Регистратор'
        verbose_name_plural = 'Регистраторы'

    def save(self, *args, **kwargs):
        if not self.pk:

            self.role = User.Role.REGISTRAR
            self.is_staff = True
            password = generate_password_and_notify(self.username)
            self.set_password(password)
        super().save(*args, **kwargs)
        group = Group.objects.get(name='Регистраторы')
        self.groups.add(group)

    def __str__(self):
        return super().get_full_name()


class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.DOCTOR)


class Doctor(User):
    objects = DoctorManager()

    @property
    def properties(self):
        return self.doctorproperties

    def get_schedule_for_date(self, date):
        # проверяем наличие исключения для данной даты
        exception_qs = self.scheduleexception_set.filter(
            start_date__lte=date, end_date__gte=date).order_by('-id')
        if exception_qs.exists():
            exception = exception_qs.first()
            if exception.start_time and exception.end_time:
                return exception.start_time, exception.end_time
            else:
                return None, None
        # получаем расписание врача с диапазоном дат, которое включает заданную дату
        schedule_qs = self.schedules.filter(
            start_date__lte=date, end_date__gte=date)

        if schedule_qs.exists():
            # берем первое расписание, которое попадает в диапазон дат
            schedule = schedule_qs.first()
            # получаем название дня недели
            weekday_name = date.strftime('%A').lower()

            # получаем время начала и конца работы в заданный день
            start_time = getattr(schedule, f"{weekday_name}_start", None)
            end_time = getattr(schedule, f"{weekday_name}_end", None)

            if start_time is None:
                return None, None
            else:
                return start_time, end_time

        return None, None  # если расписание врача на заданный день не найдено

    def get_schedule_for_date_str(self, date):
        start_time, end_time = self.get_schedule_for_date(date)
        if start_time and end_time:
            return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        else:
            return "не работает"

    def get_available_slots(self, date):
        print(date)
        start_time, end_time = self.get_schedule_for_date(date)

        if start_time is None or date < date.today():
            return []

        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)

        appointment_duration = timedelta(
            minutes=self.properties.speciality.interval)
        appointments = self.doctor_appointments.filter(date=date)

        # Поиск всех занятых слотов на запись
        busy_slots = []
        for appointment in appointments:
            appointment_start = datetime.combine(date, appointment.time)
            appointment_end = appointment_start + appointment_duration
            busy_slots.append((appointment_start, appointment_end))

        # Поиск всех доступных слотов на запись
        available_slots = []
        current_slot_start = start_datetime
        now = datetime.now()
        while current_slot_start + appointment_duration <= end_datetime:
            current_slot_end = current_slot_start + appointment_duration
            current_slot_busy = False

            for busy_start, busy_end in busy_slots:
                if current_slot_start < busy_end and busy_start < current_slot_end:
                    current_slot_busy = True
                    break

            if not current_slot_busy and (date > date.today() or current_slot_end > now):
                available_slots.append(current_slot_start.time())

            current_slot_start += appointment_duration

        return available_slots

    class Meta:
        proxy = True
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def save(self, *args, **kwargs):
        if not self.pk:

            self.role = User.Role.DOCTOR
            password = generate_password_and_notify(self.username)
            self.set_password(password)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.doctorproperties.speciality}: {self.last_name} {self.first_name} {self.patronymic}'


class DoctorProperties(models.Model):
    class Meta:
        verbose_name = 'Данные медработника'
        verbose_name_plural = 'Данные медработника'

    def __str__(self) -> str:
        return self.doctor.__str__()

    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    image = models.ImageField('Фотография', null=True, blank=True)
    speciality = models.ForeignKey(
        Speciality, verbose_name='Специальность', on_delete=models.SET_NULL, null=True)
    visible = models.BooleanField('Видимость для пациентов', default=False)
    cabinet = models.CharField(
        'Кабинет', max_length=50, blank=False, default='-')

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image.path)
            if img.width > img.height:
                # Обрезаем изображение по вертикали, если ширина больше высоты
                left = (img.width - img.height) // 2
                right = left + img.height
                top = 0
                bottom = img.height
            else:
                # Обрезаем изображение по горизонтали, если высота больше ширины
                left = 0
                right = img.width
                top = (img.height - img.width) // 2
                bottom = top + img.width

            img = img.crop((left, top, right, bottom))

            # Устанавливаем размер изображения (необязательно)
            img.thumbnail((250, 250))

            # Сохраняем обрезанное изображение
            img.save(self.image.path)
        super().save(*args, **kwargs)


class PatientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.PATIENT)


class Patient(User):
    objects = PatientManager()

    @property
    def properties(self):
        return self.patientproperties

    class Meta:
        proxy = True
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.role = User.Role.PATIENT
                password = generate_password_and_notify(self.username)
                self.set_password(password)
            super().save(*args, **kwargs)
        except Exception as e:
            print(e)

    def __str__(self):
        return f'ID {self.id}: {self.last_name} {self.first_name} {self.patronymic}'


class PatientProperties(models.Model):
    class Meta:
        verbose_name = 'Данные пациента'
        verbose_name_plural = 'Данные пациента'

    def __str__(self) -> str:
        return self.patient.__str__()
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    address = models.CharField('Адрес проживания', max_length=128)
    contract_number = models.CharField(
        'Номер договора', max_length=20, blank=True)
    passport_number = models.CharField(
        'Номер паспорта', max_length=10, blank=True)
