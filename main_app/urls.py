from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/create/', views.create_vacancy, name='create_vacancy'),
    path('vacancy/<int:pk>/apply/', views.apply_to_vacancy, name='apply_to_vacancy'),
    path('vacancy/<int:pk>/applications/', views.vacancy_applications, name='vacancy_applications'),

    path('application/<int:pk>/update/', views.update_application_status, name='update_application_status'),
    path('company/create/', views.create_company, name='create_company'),
    path('company/edit/', views.company_edit, name='company_edit'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),

    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-vacancies/', views.my_vacancies, name='my_vacancies'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main_app/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main_app:home'), name='logout'),
]