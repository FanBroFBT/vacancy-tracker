from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

app_name = 'api'

urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    path('logout/', api_views.logout_token, name='token-logout'),
    path('vacancies/', api_views.VacancyListCreateAPIView.as_view(), name='vacancy-list-create'),
    path('vacancies/search/', api_views.vacancy_search, name='vacancy-search'),
    path('vacancies/<int:pk>/', api_views.VacancyDetailAPIView.as_view(), name='vacancy-detail'),
    path('my-applications/', api_views.my_applications, name='my-applications'),
    path('applications/<int:pk>/status/', api_views.update_application_status, name='application-status'),
]