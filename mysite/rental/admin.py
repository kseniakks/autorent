
from django.contrib import admin
from .models import (
    CarClass,
    Tariff,
    Car,
    Client,
    DriverLicense,
    Rental,
    ReturnInspection,
    DamageFine,
    RentalFine,
)


@admin.register(CarClass)
class CarClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_day', 'deposit')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_class', 'tariff', 'status', 'mileage')
    list_filter = ('status', 'car_class')
    search_fields = ('name',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email')
    search_fields = ('full_name', 'phone', 'email')


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'issue_date')
    search_fields = ('number', 'client__full_name')


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        'car', 'client', 'start_date',
        'end_date', 'status', 'total_price', 'deposit'
    )
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('car__name', 'client__full_name')


@admin.register(ReturnInspection)
class ReturnInspectionAdmin(admin.ModelAdmin):
    list_display = ('rental', 'return_date', 'mileage', 'condition')


@admin.register(DamageFine)
class DamageFineAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(RentalFine)
class RentalFineAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'damage', 'amount')
