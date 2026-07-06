from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancies/<int:pk>/apply/', views.apply_to_vacancy, name='apply_to_vacancy'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('profile/', views.profile, name='profile'),
    path('my-applications/', views.my_applications, name='my_applications'),
]