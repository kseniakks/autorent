
from django.db import models
from django.conf import settings


class CarClass(models.Model):
    name = models.CharField(max_length=100, verbose_name='Класс автомобиля')
    description = models.TextField(blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Класс автомобиля'
        verbose_name_plural = 'Классы автомобилей'


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название тарифа')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за день')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Залог')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

class Car(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('rented', 'Арендован'),
        ('repair', 'В ремонте'),
    ]

    GEARBOX_CHOICES = [
        ('Автомат', 'Автомат'),
        ('Механика', 'Механика'),
    ]

    name = models.CharField(
        max_length=150,
        verbose_name='Автомобиль'
    )

    car_class = models.ForeignKey(
        CarClass,
        on_delete=models.PROTECT,
        verbose_name='Класс'
    )

    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.PROTECT,
        verbose_name='Тариф'
    )

    year = models.PositiveIntegerField(
        default=2022,
        verbose_name='Год выпуска'
    )

    gearbox = models.CharField(
        max_length=30,
        choices=GEARBOX_CHOICES,
        default='Автомат',
        verbose_name='Коробка передач'
    )

    image = models.URLField(
        blank=True,
        verbose_name='Ссылка на фотографию'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Статус'
    )

    mileage = models.PositiveIntegerField(
        default=0,
        verbose_name='Пробег'
    )
    seats = models.PositiveIntegerField(
        default=5,
        verbose_name='Количество мест'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'



class Client(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_profile',
        verbose_name='Аккаунт пользователя'
    )
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Электронная почта')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class DriverLicense(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    number = models.CharField(max_length=30, unique=True, verbose_name='Номер удостоверения')
    issue_date = models.DateField(verbose_name='Дата выдачи')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'


class Rental(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Забронирована'),
        ('issued', 'Выдана'),
        ('returned', 'Возвращена'),
        ('cancelled', 'Отменена'),
    ]

    car = models.ForeignKey(Car, on_delete=models.PROTECT, verbose_name='Автомобиль')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name='Клиент')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked', verbose_name='Статус')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Залог')

    def __str__(self):
        return f'{self.car} — {self.client}'

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'


class ReturnInspection(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, verbose_name='Аренда')
    return_date = models.DateField(auto_now_add=True, verbose_name='Дата возврата')
    mileage = models.PositiveIntegerField(verbose_name='Пробег при возврате')
    condition = models.TextField(verbose_name='Состояние автомобиля')

    def __str__(self):
        return f'Осмотр: {self.rental}'

    class Meta:
        verbose_name = 'Осмотр при возврате'
        verbose_name_plural = 'Осмотры при возврате'


class DamageFine(models.Model):
    name = models.CharField(max_length=150, verbose_name='Повреждение')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость штрафа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Штраф за повреждение'
        verbose_name_plural = 'Штрафы за повреждения'


class RentalFine(models.Model):
    inspection = models.ForeignKey(ReturnInspection, on_delete=models.CASCADE, verbose_name='Осмотр')
    damage = models.ForeignKey(DamageFine, on_delete=models.PROTECT, verbose_name='Повреждение')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма штрафа')

    def __str__(self):
        return f'{self.damage} — {self.amount}'

    class Meta:
        verbose_name = 'Начисленный штраф'
        verbose_name_plural = 'Начисленные штрафы'

