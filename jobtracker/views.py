from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Company, Vacancy, Application
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CategorySerializer, CompanySerializer, VacancySerializer, ApplicationSerializer,
    VacancySearchSerializer, ApplicationStatusUpdateSerializer,
)

# =========================================================
#  АУТЕНТИФИКАЦИЯ (токен-based login / logout / register)
# =========================================================

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Регистрация нового пользователя."""
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"error": "username и password обязательны"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Пользователь уже существует"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Логин: возвращает токен по username/password."""
    from django.contrib.auth import authenticate
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Неверные учётные данные"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Логаут: удаляет токен текущего пользователя."""
    request.user.auth_token.delete()
    return Response({"message": "Вы вышли из системы"}, status=status.HTTP_200_OK)


# =========================================================
#  FBV с DRF-декораторами (>=2 требуется)
# =========================================================

@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def vacancy_list_create(request):
    """FBV: список вакансий (с фильтрацией) + создание новой вакансии."""
    if request.method == "GET":
        search = VacancySearchSerializer(data=request.query_params)
        search.is_valid(raise_exception=True)
        qs = Vacancy.objects.active()

        keyword = search.validated_data.get("keyword")
        category = search.validated_data.get("category")
        location = search.validated_data.get("location")
        employment_type = search.validated_data.get("employment_type")

        if keyword:
            qs = qs.filter(title__icontains=keyword)
        if category:
            qs = qs.filter(category__name__icontains=category)
        if location:
            qs = qs.filter(location__icontains=location)
        if employment_type:
            qs = qs.filter(employment_type=employment_type)

        serializer = VacancySerializer(qs, many=True)
        return Response(serializer.data)

    # POST — создание вакансии, привязка к текущему пользователю
    serializer = VacancySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(posted_by=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def vacancy_detail(request, pk):
    """FBV: полный CRUD (Retrieve/Update/Delete) для одной вакансии."""
    try:
        vacancy = Vacancy.objects.get(pk=pk)
    except Vacancy.DoesNotExist:
        return Response({"error": "Вакансия не найдена"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(VacancySerializer(vacancy).data)

    if vacancy.posted_by != request.user:
        return Response({"error": "Нет прав на изменение"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PUT":
        serializer = VacancySerializer(vacancy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    if request.method == "DELETE":
        vacancy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =========================================================
#  CBV на APIView (>=2 требуется)
# =========================================================

class CompanyListCreateAPIView(APIView):
    """CBV: список компаний + создание новой."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        companies = Company.objects.all()
        return Response(CompanySerializer(companies, many=True).data)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationListCreateAPIView(APIView):
    """CBV: мои отклики (GET) + отклик на вакансию (POST), привязка к request.user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(applicant=request.user)
        return Response(ApplicationSerializer(applications, many=True).data)

    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(applicant=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicationStatusUpdateAPIView(APIView):
    """CBV (бонус): работодатель обновляет статус отклика на свою вакансию."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response({"error": "Отклик не найден"}, status=status.HTTP_404_NOT_FOUND)

        if application.vacancy.posted_by != request.user:
            return Response({"error": "Нет прав"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ApplicationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application.status = serializer.validated_data["status"]
        application.save()
        return Response(ApplicationSerializer(application).data)


# =========================================================
#  Category — простой список (вспомогательный эндпоинт)
# =========================================================

@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def category_list_create(request):
    if request.method == "GET":
        return Response(CategorySerializer(Category.objects.all(), many=True).data)
    serializer = CategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)