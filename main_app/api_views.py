from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Vacancy, Application
from .serializers import (
    VacancySerializer,
    ApplicationSerializer,
    VacancySearchSerializer,
    ApplicationStatusUpdateSerializer,
)
from .permissions import (
    IsEmployerOrReadOnly,
    IsVacancyOwnerOrReadOnly,
    IsVacancyOwnerForStatusUpdate,
)


class VacancyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = VacancySerializer
    permission_classes = [IsEmployerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class VacancyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsEmployerOrReadOnly, IsVacancyOwnerOrReadOnly]


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def my_applications(request):
    if request.method == 'GET':
        applications = Application.objects.filter(
            applicant=request.user
        ).order_by('-applied_at')
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        vacancy = get_object_or_404(Vacancy, pk=request.data.get('vacancy'))
        if Application.objects.filter(vacancy=vacancy, applicant=request.user).exists():
            return Response(
                {'detail': 'Вы уже откликались на эту вакансию.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(applicant=request.user, vacancy=vacancy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated, IsVacancyOwnerForStatusUpdate])
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    from rest_framework.exceptions import PermissionDenied
    if application.vacancy.company.owner_id != request.user.id:
        raise PermissionDenied("Вы не являетесь владельцем этой вакансии.")

    serializer = ApplicationStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        application.status = serializer.validated_data['status']
        application.save()
        return Response(ApplicationSerializer(application).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def vacancy_search(request):
    params = VacancySearchSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)

    vacancies = Vacancy.objects.filter(is_active=True)
    city = params.validated_data.get('city')
    level = params.validated_data.get('level')
    if city:
        vacancies = vacancies.filter(city__icontains=city)
    if level:
        vacancies = vacancies.filter(level=level)

    return Response(VacancySerializer(vacancies, many=True).data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_token(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)