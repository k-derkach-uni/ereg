from django.contrib import admin
from django.forms import inlineformset_factory

from appointments.forms import AppointmentForm
from .models import *
from appointments.models import *

from schedule.models import *
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from schedule.forms import *
from django.urls import reverse
from django.utils.html import format_html
from .forms import *
from payments.models import *


admin.site.index_title = 'Панель управления'
admin.site.site_header = 'Панель управления'
admin.site.site_title = 'Панель управления'


class DoctorPropertiesInline(admin.StackedInline):
    model = DoctorProperties


class PatientPropertiesInline(admin.StackedInline):
    model = PatientProperties


class CustomUserAdmin(UserAdmin):

    def get_full_name(self, obj):
        return obj.get_full_name()  # вызываем метод модели
    get_full_name.short_description = 'ФИО'

    list_display = ['get_full_name', 'role']

    search_fields = ['first_name', 'last_name', 'role']

    fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': (
            'last_name', 'first_name', 'patronymic',  'sex', 'birth_date', 'phone_number')}),
        (_('Permissions'), {'fields': (
            'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': (
            'last_name', 'first_name', 'patronymic', 'sex', 'birth_date', 'phone_number')}),
        (_('Permissions'), {'fields': (
            'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class RegAdmin(admin.ModelAdmin):
    model = Registrar

    def get_full_name(self, obj):
        return obj.get_full_name()  # вызываем метод модели
    get_full_name.short_description = 'ФИО'

    search_fields = ['first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': (
            'last_name', 'first_name', 'patronymic', 'sex', 'birth_date', 'phone_number')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': (
            'last_name', 'first_name', 'patronymic', 'sex', 'birth_date', 'phone_number')}),
    )


class DoctorAdmin(admin.ModelAdmin):
    model = Doctor

    def get_full_name(self, obj):
        return obj.get_full_name()  # вызываем метод модели
    get_full_name.short_description = 'ФИО'

    def get_speciality_name(self, obj):
        return obj.doctorproperties.speciality.name
    get_speciality_name.short_description = 'Специальность'

    def get_cabinet(self, obj):
        return obj.doctorproperties.cabinet
    get_cabinet.short_description = 'Кабинет'

    list_display = ['get_full_name', 'get_speciality_name', 'get_cabinet']

    search_fields = ['first_name', 'last_name',
                     'doctorproperties__speciality__name', 'doctorproperties__cabinet']
    fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'patronymic',
                                         'sex', 'birth_date', 'phone_number')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'patronymic',
                                         'sex', 'birth_date', 'phone_number')}),
    )

    inlines = (DoctorPropertiesInline,)
    # exclude = ('role','date_joined','groups',
    #     'user_permissions','is_superuser','is_staff',
    #     'last_login','is_active')


class PatientAdmin(admin.ModelAdmin):
    model = Patient

    def get_full_name(self, obj):
        return obj.get_full_name()  # вызываем метод модели
    get_full_name.short_description = 'ФИО'

    list_display = ['get_full_name', 'id', 'username']

    search_fields = ['first_name', 'last_name', 'id', 'username']
    fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'patronymic',
                                         'sex', 'birth_date', 'phone_number')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', )}),
        (_('Personal info'), {'fields': ('last_name', 'first_name', 'patronymic',
                                         'sex', 'birth_date', 'phone_number')}),
    )

    inlines = (PatientPropertiesInline,)
    # exclude = ('role','date_joined','groups',
    #     'user_permissions','is_superuser','is_staff',
    #     'last_login','is_active')


class ScheduleExceptionAdmin(admin.ModelAdmin):
    model = ScheduleException
    list_display = ('doctor', 'start_date', 'end_date',
                    'start_time', 'end_time')
    search_fields = ('doctor__first_name', 'doctor__last_name')


class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm
    add_form = AppointmentForm

    change_form_template = 'appointment/change_form.html'  # Указываем имя шаблона

    autocomplete_fields = ['doctor', 'patient']
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    search_fields = ('patient__id', 'patient__first_name', 'patient__last_name',
                     'doctor__first_name', 'doctor__last_name', 'doctor__doctorproperties__speciality__name')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleForm
    fieldsets = (
        (None, {
            'fields': ('name', 'doctors', 'start_date', 'end_date')
        }),
        ('Понедельник', {
            'fields': (('monday_start', 'monday_end'), )
        }),
        ('Вторник', {
            'fields': (('tuesday_start', 'tuesday_end'), )
        }),
        ('Среда', {
            'fields': (('wednesday_start', 'wednesday_end'), )
        }),
        ('Четверг', {
            'fields': (('thursday_start', 'thursday_end'), )
        }),
        ('Пятница', {
            'fields': (('friday_start', 'friday_end'), )
        }),
        ('Суббота', {
            'fields': (('saturday_start', 'saturday_end'), )
        }),
        ('Воскресенье', {
            'fields': (('sunday_start', 'sunday_end'),)
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Speciality)


class ServiceAdmin(admin.ModelAdmin):
    search_fields = ['name__icontains']


admin.site.register(Service, ServiceAdmin)


class InvoiceServiceInline(admin.TabularInline):
    model = InvoiceService
    extra = 1
    autocomplete_fields = ['service']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['service'].widget.can_change_related = False
        formset.form.base_fields['service'].widget.attrs[
            'onchange'] = 'updatePrice(this)'
        formset.form.base_fields['quantity'].widget.attrs[
            'onchange'] = 'updateTotalPrice(this)'
        return formset

    def total_price(self, instance):
        service = instance.service
        quantity = instance.quantity
        return service.price * quantity if service and quantity else 0

    class Media:
        js = ('admin/js/invoice_service_inline.js',)


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceServiceInline]

    list_display = ('patient', 'doctor', 'creation_date',
                    'payment_date', 'status')
    # search_fields = ('doctor__first_name', 'doctor__last_name')

    autocomplete_fields = ['doctor', 'patient']
    exclude = ['payment_date']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        # Если объект уже существует и его статус "оплачено", делаем все поля только для чтения
        if obj and obj.status == "CONFIRMED":
            # Укажите здесь реальные имена полей, которые хотите сделать только для чтения
            readonly_fields += ('patient', 'doctor',
                                'services', 'total_amount', 'status')

        return readonly_fields


admin.site.register(Invoice, InvoiceAdmin)


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)

admin.site.register(Registrar, RegAdmin)
admin.site.register(ScheduleException, ScheduleExceptionAdmin)


admin.site.register(Appointment, AppointmentAdmin)
