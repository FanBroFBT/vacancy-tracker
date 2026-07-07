from rest_framework import serializers
from .models import Category, Company, Vacancy, Application


# ---------- ModelSerializer (>=2 требуется) ----------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "description", "website", "logo_url", "created_at"]


class VacancySerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.name")
    category_name = serializers.ReadOnlyField(source="category.name")
    posted_by = serializers.ReadOnlyField(source="posted_by.username")

    class Meta:
        model = Vacancy
        fields = [
            "id", "title", "description", "company", "company_name",
            "category", "category_name", "location", "employment_type",
            "salary_min", "salary_max", "deadline", "posted_by", "created_at",
        ]
        read_only_fields = ["posted_by"]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.ReadOnlyField(source="applicant.username")
    vacancy_title = serializers.ReadOnlyField(source="vacancy.title")

    class Meta:
        model = Application
        fields = ["id", "vacancy", "vacancy_title", "applicant", "cover_letter", "status", "applied_at"]
        read_only_fields = ["applicant", "status"]


# ---------- Обычный Serializer (>=2 требуется, НЕ ModelSerializer) ----------

class VacancySearchSerializer(serializers.Serializer):
    """Валидация параметров поиска/фильтра вакансий (не привязан к модели напрямую)."""
    keyword = serializers.CharField(max_length=100, required=False, allow_blank=True)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    location = serializers.CharField(max_length=120, required=False, allow_blank=True)
    employment_type = serializers.ChoiceField(
        choices=Vacancy.EMPLOYMENT_CHOICES, required=False
    )


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    """Валидация обновления статуса отклика (используется работодателем)."""
    status = serializers.ChoiceField(choices=Application.STATUS_CHOICES)