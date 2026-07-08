from rest_framework import serializers
from .models import Vacancy, Application


class VacancySerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'description', 'requirements', 'level',
            'city', 'company', 'company_name', 'created_at', 'is_active',
        ]
        read_only_fields = ['company', 'created_at']


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.ReadOnlyField(source='applicant.username')
    vacancy_title = serializers.ReadOnlyField(source='vacancy.title')

    class Meta:
        model = Application
        fields = [
            'id', 'vacancy', 'vacancy_title', 'applicant', 'applicant_username',
            'message', 'status', 'applied_at',
        ]
        read_only_fields = ['applicant', 'status', 'applied_at']


class VacancySearchSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=50, required=False, allow_blank=True)
    level = serializers.ChoiceField(
        choices=Vacancy.LEVEL_CHOICES, required=False, allow_blank=True
    )


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.STATUS)

    def validate_status(self, value):
        if value == 'send':
            raise serializers.ValidationError(
                "Нельзя вручную вернуть статус в 'send'."
            )
        return value