from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('applicant', 'Applicant'),
        ('employer', 'Employer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='profile_images/',blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    

class Company(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logo/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return f"{self.logo} {self.name}"

class Vacancy(models.Model):
    LEVEL_CHOICES = [
        ('intern', 'Intern'),
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    requirements = models.CharField(max_length=300, blank=True)
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Vacancies"

    def __str__(self):
        return f"{self.title} {self.company} {self.is_active} {self.created_at}"

class Application(models.Model):
    STATUS = [
        ('send', 'Send'),
        ('seen', 'Seen'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='send')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vacancy} {self.applicant} {self.status} {self.applied_at}"