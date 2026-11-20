from datetime import date, datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import BookingForm


def home(request):
    return render(request, 'index.html')


def catalog(request):
    cars = [
        {
            'id': 1,
            'name': 'Kia Rio',
            'year': 2022,
            'car_class': 'Эконом',
            'gearbox': 'Автомат',
            'price': 2500,
            'image': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=30),
        },
        {
            'id': 2,
            'name': 'Hyundai Solaris',
            'year': 2023,
            'car_class': 'Эконом',
            'gearbox': 'Механика',
            'price': 2200,
            'image': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=700',
            'status': 'rented',
            'available_until': date.today() + timedelta(days=5),
        },
        {
            'id': 3,
            'name': 'Toyota Camry',
            'year': 2023,
            'car_class': 'Комфорт',
            'gearbox': 'Автомат',
            'price': 4500,
            'image': 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=20),
        },
        {
            'id': 4,
            'name': 'BMW 3 Series',
            'year': 2022,
            'car_class': 'Бизнес',
            'gearbox': 'Автомат',
            'price': 6500,
            'image': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=700',
            'status': 'repair',
            'available_until': date.today() + timedelta(days=10),
        },
        {
            'id': 5,
            'name': 'Volkswagen Polo',
            'year': 2021,
            'car_class': 'Эконом',
            'gearbox': 'Механика',
            'price': 2000,
            'image': 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=15),
        },
        {
            'id': 6,
            'name': 'Mercedes-Benz E-Class',
            'year': 2023,
            'car_class': 'Бизнес',
            'gearbox': 'Автомат',
            'price': 8000,
            'image': 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=25),
        },
    ]
    car_class = request.GET.get('class', '')
    gearbox = request.GET.get('gearbox', '')
    max_price = request.GET.get('max_price', '')

    if car_class:
        cars = [car for car in cars if car['car_class'] == car_class]

    if gearbox:
        cars = [car for car in cars if car['gearbox'] == gearbox]

    if max_price:
        try:
            cars = [car for car in cars if car['price'] <= int(max_price)]
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


def booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            messages.success(
                request,
                'Заявка успешно отправлена! Мы свяжемся с вами.'
            )
            return redirect('/booking/')

    else:
        initial_data = {
            'car_name': request.GET.get('car', ''),
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
        }
        form = BookingForm(initial=initial_data)

    return render(request, 'booking.html', {'form': form})


def profile(request):
    active_rent = {
        'car_name': 'Kia Rio',
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=5),
        'price': 2500,
        'status': 'Активна',
    }

    rent_history = [
        {
            'car_name': 'BMW 3 Series',
            'price': 6500,
            'status': 'Завершена',
            'mileage': 32150.0,
            'condition': 'Обнаружена царапина на двери',
            'fine': 1500,
        },
    ]

    return render(request, 'profile.html', {
        'active_rent': active_rent,
        'rent_history': rent_history,
    })


def rules(request):
    return render(request, 'rules.html')
def search(request):
    cars = [
        {
            'id': 1,
            'name': 'Kia Rio',
            'year': 2022,
            'car_class': 'Эконом',
            'gearbox': 'Автомат',
            'price': 2500,
            'image': 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=30),
        },
        {
            'id': 2,
            'name': 'Hyundai Solaris',
            'year': 2023,
            'car_class': 'Эконом',
            'gearbox': 'Механика',
            'price': 2200,
            'image': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=700',
            'status': 'rented',
            'available_until': date.today() + timedelta(days=5),
        },
        {
            'id': 3,
            'name': 'Toyota Camry',
            'year': 2023,
            'car_class': 'Комфорт',
            'gearbox': 'Автомат',
            'price': 4500,
            'image': 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=20),
        },
        {
            'id': 4,
            'name': 'BMW 3 Series',
            'year': 2022,
            'car_class': 'Бизнес',
            'gearbox': 'Автомат',
            'price': 6500,
            'image': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=700',
            'status': 'repair',
            'available_until': date.today() + timedelta(days=10),
        },
        {
            'id': 5,
            'name': 'Volkswagen Polo',
            'year': 2021,
            'car_class': 'Эконом',
            'gearbox': 'Механика',
            'price': 2000,
            'image': 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=15),
        },
        {
            'id': 6,
            'name': 'Mercedes-Benz E-Class',
            'year': 2023,
            'car_class': 'Бизнес',
            'gearbox': 'Автомат',
            'price': 8000,
            'image': 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=700',
            'status': 'available',
            'available_until': date.today() + timedelta(days=25),
        },
    ]

    selected_class = request.GET.get('class', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    errors = []
    search_end_date = None

    if selected_class:
        cars = [
            car for car in cars
            if car['car_class'] == selected_class
        ]

    if start_date or end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            search_end_date = datetime.strptime(
                end_date, '%Y-%m-%d'
            ).date()

            if start < date.today():
                errors.append('Дата начала не может быть в прошлом.')

            if search_end_date <= start:
                errors.append('Дата возврата должна быть позже даты получения.')

        except ValueError:
            errors.append('Укажите обе даты аренды в правильном формате.')

    if not errors:
        cars = [
            car for car in cars
            if car['status'] == 'available'
        ]

        if search_end_date:
            cars = [
                car for car in cars
                if car['available_until'] >= search_end_date
            ]

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
