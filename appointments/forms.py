from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from users.models import *
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    time = forms.TimeField(label='Время', widget=forms.Select(choices=()))

    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.date and self.instance.time:
            doctor = self.instance.doctor
            date = self.instance.date
            available_slots = doctor.get_available_slots(date)

            self.fields['time'].widget.choices = [
                (slot.strftime('%H:%M'), slot.strftime('%H:%M')) for slot in available_slots]
            if self.instance.time:
                self.fields['time'].widget.choices.append(
                    (self.instance.time, self.instance.time))

        else:
            self.fields['time'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            date = date.strftime('%Y-%m-%d')
            cleaned_data['date'] = datetime.strptime(date, '%Y-%m-%d').date()

        return cleaned_data
