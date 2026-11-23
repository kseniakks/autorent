
from django import forms
from datetime import date
import re


class BookingForm(forms.Form):

    car_name = forms.CharField(
        label='Автомобиль',
        max_length=100,
        required=True
    )

    start_date = forms.DateField(
        label='Дата получения',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    end_date = forms.DateField(
        label='Дата возврата',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    full_name = forms.CharField(
        label='ФИО',
        max_length=150,
        min_length=2,
        required=True
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        required=True
    )

    email = forms.EmailField(
        label='Электронная почта',
        required=True
    )

    license_number = forms.CharField(
        label='Номер водительского удостоверения',
        max_length=30,
        required=True
    )

    license_date = forms.DateField(
        label='Дата выдачи удостоверения',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    # Проверка даты получения
    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']

        if start_date < date.today():
            raise forms.ValidationError(
                'Дата получения не может быть в прошлом.'
            )

        return start_date

    # Проверка даты возврата
    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        start_date = self.cleaned_data.get('start_date')

        if start_date and end_date <= start_date:
            raise forms.ValidationError(
                'Дата возврата должна быть позже даты получения.'
            )

        return end_date

    # Проверка телефона
    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = re.sub(r'\D', '', phone)

        if not re.fullmatch(r'[+\d()\-\s]+', phone):
            raise forms.ValidationError(
                'Некорректный формат телефона.'
            )

        if not 10 <= len(digits) <= 15:
            raise forms.ValidationError(
                'Телефон должен содержать от 10 до 15 цифр.'
            )

        return phone

    # Проверка даты выдачи прав
    def clean_license_date(self):
        license_date = self.cleaned_data['license_date']

        if license_date > date.today():
            raise forms.ValidationError(
                'Дата выдачи удостоверения не может быть в будущем.'
            )

        return license_date


from .models import DamageFine


class ReturnCarForm(forms.Form):
    mileage = forms.IntegerField(
        label='Пробег при возврате',
        min_value=0,
        required=True
    )

    condition = forms.CharField(
        label='Состояние автомобиля',
        widget=forms.Textarea(attrs={'rows': 4}),
        min_length=3,
        required=True
    )

    damages = forms.ModelMultipleChoiceField(
        label='Обнаруженные повреждения',
        queryset=DamageFine.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

