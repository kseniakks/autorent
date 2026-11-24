
from django import forms
from datetime import date
import re


class BookingForm(forms.Form):

    car_name = forms.CharField(
        label='Автомобиль',
        max_length=100,
        required=True,
        error_messages={
            'required': 'Выберите автомобиль. Это поле обязательно для заполнения.',
            'max_length': 'Название автомобиля слишком длинное. Укажите название короче.'
        }
    )

    start_date = forms.DateField(
        label='Дата получения',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        error_messages={
            'required': 'Укажите дату получения автомобиля.',
            'invalid': 'Введите корректную дату получения.'
        }
    )

    end_date = forms.DateField(
        label='Дата возврата',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        error_messages={
            'required': 'Укажите дату возврата автомобиля.',
            'invalid': 'Введите корректную дату возврата.'
        }
    )

    full_name = forms.CharField(
        label='ФИО',
        max_length=150,
        min_length=2,
        required=True,
        error_messages={
            'required': 'Введите ФИО.',
            'min_length': 'ФИО должно содержать минимум 2 символа.',
            'max_length': 'ФИО слишком длинное. Сократите его.'
        }
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        required=True,
        error_messages={
            'required': 'Введите номер телефона.',
            'max_length': 'Номер телефона слишком длинный.'
        }
    )
    email = forms.EmailField(
        label='Электронная почта',
        required=True,
        error_messages={
            'required': 'Введите адрес электронной почты.',
            'invalid': 'Некорректный адрес. Пример правильного адреса: example@mail.ru.'
        }
    )

    license_number = forms.CharField(
        label='Номер водительского удостоверения',
        max_length=30,
        required=True,
        error_messages={
            'required': 'Введите номер водительского удостоверения.',
            'max_length': 'Номер слишком длинный. Проверьте введённые данные.'
        }
    )

    license_date = forms.DateField(
        label='Дата выдачи удостоверения',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        error_messages={
            'required': 'Укажите дату выдачи водительского удостоверения.',
            'invalid': 'Введите корректную дату выдачи удостоверения.'
        }
    )

    # Проверка даты получения
    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']

        if start_date < date.today():
            raise forms.ValidationError(
                'Дата получения не может быть в прошлом. Выберите сегодняшнюю или более позднюю дату.'
            )

        return start_date

    
    # Проверка даты возврата
    def clean_end_date(self):
        return self.cleaned_data['end_date']

    # Общая проверка нескольких полей
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            self.add_error(
                'end_date',
                'Дата возврата должна быть позже даты получения. Выберите более позднюю дату.'
            )

        return cleaned_data


    # Проверка телефона
    
    # Проверка телефона
    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = re.sub(r'\D', '', phone)

        if not re.fullmatch(r'[+\d()\-\s]+', phone):
            raise forms.ValidationError(
                'Некорректный формат телефона. '
                'Используйте цифры, пробелы, скобки или знак +.'
            )

        if not 10 <= len(digits) <= 15:
            raise forms.ValidationError(
                'Неверная длина номера. '
                'Введите от 10 до 15 цифр.'
            )

        return phone


    # Проверка даты выдачи прав
    
    # Проверка даты выдачи прав
    def clean_license_date(self):
        license_date = self.cleaned_data['license_date']

        if license_date > date.today():
            raise forms.ValidationError(
                'Дата выдачи удостоверения не может быть в будущем. '
                'Укажите фактическую дату выдачи прав.'
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

