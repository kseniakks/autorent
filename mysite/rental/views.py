
from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import BookingForm, ReturnCarForm
from .models import (
    Car,
    Client,
    DriverLicense,
    Rental,
    ReturnInspection,
    RentalFine,
)


def home(request):
    return render(request, 'index.html')


def catalog(request):
    cars = Car.objects.select_related(
        'car_class',
        'tariff'
    ).all().order_by('id')

    car_class = request.GET.get('class', '').strip()
    gearbox = request.GET.get('gearbox', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if car_class:
        cars = cars.filter(car_class__name__iexact=car_class)

    if gearbox:
        cars = cars.filter(gearbox=gearbox)

    if max_price:
        try:
            cars = cars.filter(
                tariff__price_per_day__lte=int(max_price)
            )
        except ValueError:
            max_price = ''

    paginator = Paginator(cars, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'selected_class': car_class,
        'selected_gearbox': gearbox,
        'selected_max_price': max_price,
    }

    return render(request, 'catalog.html', context)


def catalog_api(request):
    """Возвращает найденные автомобили в формате JSON для поиска через fetch()."""
    cars = Car.objects.select_related(
        'car_class',
        'tariff'
    ).all().order_by('id')

    query = request.GET.get('q', '').strip()
    car_class = request.GET.get('class', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if query:
        cars = cars.filter(name__icontains=query)

    if car_class:
        cars = cars.filter(car_class__name__iexact=car_class)

    if max_price:
        try:
            cars = cars.filter(tariff__price_per_day__lte=int(max_price))
        except (TypeError, ValueError):
            pass

    car_ids = list(cars.values_list('id', flat=True))
    return JsonResponse({
        'cars': [{'id': car_id} for car_id in car_ids],
        'count': len(car_ids),
    })



def booking(request):
    # Передаём в шаблон автомобили, их стоимость за день и залог
    cars_for_booking = list(
        Car.objects.select_related('tariff').values(
            'name',
            'tariff__price_per_day',
            'tariff__deposit'
        )
    )

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            car_name = form.cleaned_data['car_name']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            email = form.cleaned_data['email']
            license_number = form.cleaned_data['license_number']

            with transaction.atomic():
                car = Car.objects.select_for_update().filter(
                    name__iexact=car_name
                ).first()

                if not car:
                    form.add_error(
                        'car_name',
                        'Такого автомобиля нет в базе данных.'
                    )

                elif car.status == 'repair':
                    form.add_error(
                        'car_name',
                        'Автомобиль находится в ремонте.'
                    )

                elif Rental.objects.filter(
                    car=car,
                    status__in=['booked', 'issued'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exists():
                    form.add_error(
                        'car_name',
                        'Автомобиль уже арендован на выбранные даты.'
                    )

                elif DriverLicense.objects.filter(
                    number=license_number
                ).exclude(client__email=email).exists():
                    form.add_error(
                        'license_number',
                        'Это удостоверение уже зарегистрировано у другого клиента.'
                    )

                else:
                    client = None

                    if request.user.is_authenticated:
                        client = Client.objects.filter(
                            user=request.user
                        ).first()

                    if client is None:
                        client = Client.objects.filter(
                            email=email,
                            user__isnull=True
                        ).first()

                    if client is None:
                        client = Client.objects.create(
                            full_name=form.cleaned_data['full_name'],
                            phone=form.cleaned_data['phone'],
                            email=email,
                            user=(
                                request.user
                                if request.user.is_authenticated
                                else None
                            )
                        )
                    else:
                        client.full_name = form.cleaned_data['full_name']
                        client.phone = form.cleaned_data['phone']
                        client.email = email

                        if (
                            request.user.is_authenticated
                            and client.user_id is None
                        ):
                            client.user = request.user

                        client.save()

                    DriverLicense.objects.update_or_create(
                        client=client,
                        defaults={
                            'number': license_number,
                            'issue_date': form.cleaned_data['license_date'],
                        }
                    )

                    days = (end_date - start_date).days
                    total_price = car.tariff.price_per_day * days

                    Rental.objects.create(
                        car=car,
                        client=client,
                        start_date=start_date,
                        end_date=end_date,
                        total_price=total_price,
                        deposit=car.tariff.deposit,
                        status='booked'
                    )

                    send_mail(
                        subject='Бронирование автомобиля AutoRent',
                        message=(
                            f'Здравствуйте, {client.full_name}!\n\n'
                            f'Ваше бронирование успешно оформлено.\n\n'
                            f'Автомобиль: {car.name}\n'
                            f'Дата получения: {start_date}\n'
                            f'Дата возврата: {end_date}\n'
                            f'Количество дней: {days}\n'
                            f'Стоимость аренды: {total_price} руб.\n'
                            f'Залог: {car.tariff.deposit} руб.\n\n'
                            f'Статус бронирования: Ожидает выдачи.\n\n'
                            f'Спасибо, что выбрали AutoRent!'
                        ),
                        from_email=None,
                        recipient_list=[email],
                        fail_silently=True
                    )

                    messages.success(
                        request,
                        f'Аренда успешно оформлена! '
                        f'Стоимость: {total_price} руб. '
                        f'Залог: {car.tariff.deposit} руб.'
                    )

                    return redirect('booking')

    else:
        initial_data = {
            'car_name': request.GET.get('car', ''),
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
        }

        form = BookingForm(initial=initial_data)

    return render(request, 'booking.html', {
        'form': form,
        'cars_for_booking': cars_for_booking,
    })



@login_required(login_url='/accounts/login/')
def profile(request):
    # Получаем клиента, связанного с текущим аккаунтом
    client = Client.objects.filter(user=request.user).first()

    active_rentals = Rental.objects.none()
    returned_rentals = Rental.objects.none()

    if client:
        active_rentals = Rental.objects.filter(
            client=client,
            status__in=['booked', 'issued']
        ).select_related(
            'car',
            'car__tariff',
            'client'
        ).order_by('-id')

        returned_rentals = Rental.objects.filter(
            client=client,
            status='returned'
        ).select_related(
            'car',
            'car__tariff',
            'client'
        ).order_by('-id')

    active_rent = None

    if active_rentals.exists():
        rental = active_rentals.first()

        active_rent = {
            'id': rental.id,
            'car_name': rental.car.name,
            'start_date': rental.start_date,
            'end_date': rental.end_date,
            'price': rental.car.tariff.price_per_day,
            'status': rental.get_status_display(),
        }

    rent_history = []

    for rental in returned_rentals:
        inspection = ReturnInspection.objects.filter(
            rental=rental
        ).first()

        fine = 0

        if inspection:
            fine = sum(
                item.amount
                for item in RentalFine.objects.filter(
                    inspection=inspection
                )
            )

        rent_history.append({
            'car_name': rental.car.name,
            'price': rental.car.tariff.price_per_day,
            'status': rental.get_status_display(),
            'mileage': inspection.mileage if inspection else '—',
            'condition': inspection.condition if inspection else '—',
            'fine': fine,
        })

    # Передаём данные клиента в шаблон личного кабинета
    profile_name = client.full_name if client else request.user.get_full_name()

    if not profile_name:
        profile_name = request.user.username

    profile_phone = client.phone if client else 'Не указан'
    profile_email = client.email if client else (request.user.email or 'Не указан')
    profile_initial = profile_name[0].upper() if profile_name else 'U'

    return render(request, 'profile.html', {
        'active_rent': active_rent,
        'rent_history': rent_history,
        'profile_name': profile_name,
        'profile_phone': profile_phone,
        'profile_email': profile_email,
        'profile_initial': profile_initial,
    })


def rules(request):
    return render(request, 'rules.html')


def search(request):
    selected_class = request.GET.get('class', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    errors = []
    search_start_date = None
    search_end_date = None

    cars_queryset = Car.objects.select_related(
        'car_class',
        'tariff'
    ).all()

    if selected_class:
        cars_queryset = cars_queryset.filter(
            car_class__name__iexact=selected_class
        )

    if start_date or end_date:
        try:
            search_start_date = datetime.strptime(
                start_date, '%Y-%m-%d'
            ).date()

            search_end_date = datetime.strptime(
                end_date, '%Y-%m-%d'
            ).date()

            if search_start_date < date.today():
                errors.append('Дата начала не может быть в прошлом.')

            if search_end_date <= search_start_date:
                errors.append(
                    'Дата возврата должна быть позже даты получения.'
                )

        except ValueError:
            errors.append(
                'Укажите обе даты аренды в правильном формате.'
            )

    cars = []

    if not errors:
        for car in cars_queryset:
            if car.status == 'repair':
                continue

            # Если даты не указаны, показываем только свободные машины
            if not search_start_date and car.status != 'available':
                continue

            # Проверяем занятость машины на выбранные даты
            if search_start_date and search_end_date:
                has_overlap = Rental.objects.filter(
                    car=car,
                    status__in=['booked', 'issued'],
                    start_date__lte=search_end_date,
                    end_date__gte=search_start_date
                ).exists()

                if has_overlap:
                    continue

            cars.append({
                'id': car.id,
                'name': car.name,
                'year': car.year,
                'car_class': car.car_class.name,
                'gearbox': car.gearbox,
                'price': car.tariff.price_per_day,
                'image': car.image,
                'status': car.status,
                'available_until': search_end_date,
            })

    paginator = Paginator(cars, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'result_count': paginator.count,
        'selected_class': selected_class,
        'start_date': start_date,
        'end_date': end_date,
        'errors': errors,
    }

    return render(request, 'search.html', context)


@login_required(login_url='/accounts/login/')
def return_car(request, rental_id):
    rental = get_object_or_404(
        Rental.objects.select_related('car', 'client'),
        id=rental_id
    )

    # Возврат доступен владельцу аренды или менеджеру
    if (
        rental.client.user_id != request.user.id
        and not is_rental_manager(request.user)
    ):
        messages.error(
            request,
            'У вас нет доступа к этой аренде.'
        )
        return redirect('profile')

    if rental.status == 'returned':
        messages.error(request, 'Этот автомобиль уже возвращён.')
        return redirect('profile')

    if rental.status == 'cancelled':
        messages.error(
            request,
            'Нельзя оформить возврат отменённой аренды.'
        )
        return redirect('profile')

    if request.method == 'POST':
        form = ReturnCarForm(request.POST)

        if form.is_valid():
            mileage = form.cleaned_data['mileage']

            if mileage < rental.car.mileage:
                form.add_error(
                    'mileage',
                    'Пробег не может быть меньше предыдущего пробега автомобиля.'
                )
            else:
                with transaction.atomic():
                    inspection = ReturnInspection.objects.create(
                        rental=rental,
                        mileage=mileage,
                        condition=form.cleaned_data['condition']
                    )

                    for damage in form.cleaned_data['damages']:
                        RentalFine.objects.create(
                            inspection=inspection,
                            damage=damage,
                            amount=damage.price
                        )

                    rental.car.mileage = mileage
                    rental.car.status = 'available'
                    rental.car.save()

                    rental.status = 'returned'
                    rental.save()

                messages.success(
                    request,
                    'Возврат автомобиля оформлен. Штрафы рассчитаны.'
                )

                return redirect('profile')

    else:
        form = ReturnCarForm()

    return render(request, 'return_car.html', {
        'form': form,
        'rental': rental,
    })


def is_rental_manager(user):
    return (
        user.is_superuser
        or user.groups.filter(name='Менеджеры проката').exists()
    )


@login_required(login_url='/admin/login/')
@user_passes_test(is_rental_manager, login_url='/admin/login/')
def manager_rentals(request):
    rentals = Rental.objects.select_related(
        'car',
        'client'
    ).filter(
        status__in=['booked', 'issued']
    ).order_by('start_date')

    return render(request, 'manager_rentals.html', {
        'rentals': rentals,
    })


@login_required(login_url='/admin/login/')
@user_passes_test(is_rental_manager, login_url='/admin/login/')
@require_POST
def issue_rental(request, rental_id):
    with transaction.atomic():
        rental = get_object_or_404(
            Rental.objects.select_for_update().select_related('car'),
            id=rental_id
        )

        if rental.status != 'booked':
            messages.error(
                request,
                'Это бронирование уже обработано.'
            )
            return redirect('manager_rentals')

        car = Car.objects.select_for_update().get(id=rental.car_id)

        overlapping_rentals = Rental.objects.filter(
            car=car,
            status__in=['booked', 'issued'],
            start_date__lte=rental.end_date,
            end_date__gte=rental.start_date
        ).exclude(id=rental.id)

        if overlapping_rentals.exists():
            messages.error(
                request,
                'Нельзя выдать автомобиль: на эти даты уже есть другая бронь или аренда.'
            )
            return redirect('manager_rentals')

        if car.status == 'repair':
            messages.error(
                request,
                'Нельзя выдать автомобиль: он в ремонте.'
            )
            return redirect('manager_rentals')

        if car.status == 'rented':
            messages.error(
                request,
                'Нельзя выдать автомобиль: он уже арендован.'
            )
            return redirect('manager_rentals')

        rental.status = 'issued'
        rental.save(update_fields=['status'])

        car.status = 'rented'
        car.save(update_fields=['status'])

    messages.success(
        request,
        f'Автомобиль {car.name} успешно выдан клиенту.'
    )

    return redirect('manager_rentals')
