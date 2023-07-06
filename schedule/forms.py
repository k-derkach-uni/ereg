from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from .models import Schedule
from users.models import *
from django.core.exceptions import ValidationError

from django import forms
from .models import Schedule


class ScheduleForm(forms.ModelForm):
    doctors = forms.ModelMultipleChoiceField(
        queryset=Doctor.objects.order_by(
            'doctorproperties__speciality', 'last_name', 'first_name'),
        widget=FilteredSelectMultiple('специалисты', False),
        label='Медработники'
    )
    monday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False, help_text='оставьте пустым для пропуска рабочего дня')
    monday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    tuesday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False,  help_text='оставьте пустым для пропуска рабочего дня')
    tuesday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    wednesday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False,  help_text='оставьте пустым для пропуска рабочего дня')
    wednesday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    thursday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False,  help_text='оставьте пустым для пропуска рабочего дня')
    thursday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    friday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False,  help_text='оставьте пустым для пропуска рабочего дня')
    friday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    saturday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False,  help_text='оставьте пустым для пропуска рабочего дня')
    saturday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)
    sunday_start = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Начало', required=False, help_text='оставьте пустым для пропуска рабочего дня')
    sunday_end = forms.TimeField(widget=forms.TimeInput(
        attrs={'type': 'time'}), label='Конец', required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        doctors = cleaned_data.get('doctors')
        if Schedule.objects.count() > 0:
            for doctor in doctors:
                schedules = Schedule.objects.filter(
                    doctors=doctor,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                ).exclude(pk=self.instance.pk if self.instance else None)

                if schedules.exists():
                    raise ValidationError(
                        f"Расписание для работника \"{doctor}\" пересекается с другим его расписанием!"
                    )
        return cleaned_data

    class Meta:
        model = Schedule
        fields = '__all__'

    def save(self, commit=True):
        schedule = super().save(commit=False)
        if commit:
            if not schedule.id:
                schedule.save()
            schedule.doctor.set(self.cleaned_data['doctors'])
            self.save_m2m()
            schedule.save()
        return schedule
