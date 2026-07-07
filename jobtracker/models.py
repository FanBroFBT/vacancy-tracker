from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Направление/категория вакансии, например 'Backend', 'Data Science', 'Internship'."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    """Компания-работодатель."""
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VacancyManager(models.Manager):
    """Кастомный менеджер: только активные (не просроченные) вакансии."""
    def active(self):
        return self.filter(deadline__gte=timezone.now().date())


class Vacancy(models.Model):
    EMPLOYMENT_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("internship", "Internship"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="vacancies")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="vacancies")
    location = models.CharField(max_length=120, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default="internship")
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    deadline = models.DateField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_vacancies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = VacancyManager()  # кастомный менеджер (optional-пункт требований)

    def __str__(self):
        return f"{self.title} @ {self.company.name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("vacancy", "applicant")  # нельзя откликнуться дважды

    def __str__(self):
        return f"{self.applicant} -> {self.vacancy.title} ({self.status})"