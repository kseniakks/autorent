
from django.contrib import admin
from django.urls import path
from rental import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('booking/', views.booking, name='booking'),
    path('profile/', views.profile, name='profile'),
    path('rules/', views.rules, name='rules'),
    path('search/', views.search, name='search'),
]
