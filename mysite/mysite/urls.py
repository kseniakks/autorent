from django.contrib import admin
from django.urls import path, include
from rental import views
from rental import error_views

urlpatterns = [
    path('admin/', admin.site.urls),
    

    # Авторизация Django
    path('accounts/', include('django.contrib.auth.urls')),

    # Основные страницы
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('api/catalog/', views.catalog_api, name='catalog_api'),
    path('booking/', views.booking, name='booking'),
    path('profile/', views.profile, name='profile'),
    path('rules/', views.rules, name='rules'),
    path('search/', views.search, name='search'),

    # Возврат автомобиля
    path('return/<int:rental_id>/', views.return_car, name='return_car'),

    # Панель менеджера
    path('manager/rentals/', views.manager_rentals, name='manager_rentals'),
    path('manager/issue/<int:rental_id>/', views.issue_rental, name='issue_rental'),
]
handler403 = 'rental.error_views.handler403'
handler404 = 'rental.error_views.handler404'
handler500 = 'rental.error_views.handler500'