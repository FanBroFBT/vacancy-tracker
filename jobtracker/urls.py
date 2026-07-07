from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),

    # Vacancies — full CRUD (FBV)
    path("vacancies/", views.vacancy_list_create, name="vacancy-list-create"),
    path("vacancies/<int:pk>/", views.vacancy_detail, name="vacancy-detail"),

    # Companies (CBV)
    path("companies/", views.CompanyListCreateAPIView.as_view(), name="company-list-create"),

    # Categories
    path("categories/", views.category_list_create, name="category-list-create"),

    # Applications (CBV)
    path("applications/", views.ApplicationListCreateAPIView.as_view(), name="application-list-create"),
    path("applications/<int:pk>/status/", views.ApplicationStatusUpdateAPIView.as_view(), name="application-status-update"),
]