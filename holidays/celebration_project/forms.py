from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from datetime import date, timedelta


class LocationSearchForm(forms.Form):
    region = forms.ModelChoiceField(
        queryset=Regions.objects.all(),
        label='Регион',
        required=True,
    )
    people = forms.IntegerField(
        label='Количество человек',
        min_value=1,
        required=True
    )
    date = forms.DateField(
        label='Дата мероприятия',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].empty_label = "Не выбрано"

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        today = date.today()
        tomorrow = today + timedelta(days=1)
        max_date = today + timedelta(days=30)

        if selected_date < tomorrow:
            raise forms.ValidationError("Дата должна быть не раньше завтрашнего дня.")
        if selected_date > max_date:
            raise forms.ValidationError("Дата не может быть позже чем через 30 дней.")

        return selected_date


class BookingForm(forms.ModelForm):
    first_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': '',
            'id': 'first_name',
            'placeholder': 'Имя'
        }),
        required=True
    )
    last_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': '',
            'id': 'last_name',
            'placeholder': 'Фамилия'
        }),
        required=True
    )
    patronymic = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': '',
            'id': 'patronymic',
            'placeholder': 'Отчество'
        }),
        required=True
    )
    phone_num = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (___) ___ - __ - __',
            'class': ''
        }),
        required=True
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Комментарий',
            'class': ''
        }),
        required=False
    )
    total_price = forms.DecimalField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Итоговая цена',
            'class': '',
            'readonly': 'readonly',  # Делаем поле только для чтения
            'id': 'total_price'
        }),
        required=False,  # Поле будет заполняться автоматически
        decimal_places=2,
        max_digits=10
    )
    booking_services = forms.ModelMultipleChoiceField(
        queryset=Services.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': '',
            'id': 'booking_services'
        }),
        required=False,
        label='Выберите доп.услуги'
    )

    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'patronymic', 'phone_num', 'comment', 'total_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Возвращаем сам объект услуги, чтобы в шаблоне был доступ к .name, .cost и т.д.
        self.fields['booking_services'].label_from_instance = lambda obj: obj

    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get('zone')
        date = cleaned_data.get('date')

        if zone and date:
            if Booking.objects.filter(zone=zone, date=date).exists():
                raise forms.ValidationError('Эта зона уже забронирована на выбранную дату.')

        return cleaned_data


class AuthorizationUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'login',
            'name': 'login',
            'placeholder': 'Введите ваш логин'
        }),
        required=True
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'name': 'password',
            'placeholder': 'Введите ваш пароль'
        }),
        required=True
    )


class RegistrationUserForm(UserCreationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'name': 'username',
            'id': 'username',
            'placeholder': 'Придумайте логин'
        }),
        required=True
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'name': 'email',
            'id': 'email',
            'placeholder': 'Введите ваш email'
        })
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={
            'name': 'first_name',
            'id': 'first_name',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'name': 'last_name',
            'id': 'last_name',
            'placeholder': 'Введите фамилию'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'name': 'password',
            'id': 'password',
            'placeholder': 'Придумайте пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'name': 'confirm-password',
            'id': 'confirm-password',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password1', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется")
        return email
