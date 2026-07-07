from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Vacancy, Company, Application, Profile
from .forms import UserRegisterForm, ApplicationForm


def home(request):
    vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'main_app/home.html', {'vacancies': vacancies})


def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    
    city = request.GET.get('city')
    if city:
        vacancies = vacancies.filter(city__icontains=city)
    
    level = request.GET.get('level')
    if level:
        vacancies = vacancies.filter(level=level)
    
    return render(request, 'main_app/vacancy_list.html', {
        'vacancies': vacancies,
        'levels': Vacancy.LEVEL_CHOICES,
    })


def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'main_app/vacancy_detail.html', {'vacancy': vacancy})


@login_required
def apply_to_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    
    existing_application = Application.objects.filter(
        vacancy=vacancy,
        applicant=request.user
    ).exists()
    
    if existing_application:
        messages.warning(request, '⚠️ Вы уже откликались на эту вакансию!')
        return redirect('main_app:vacancy_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.applicant = request.user
            application.save()
            messages.success(request, '✅ Отклик успешно отправлен!')
            return redirect('main_app:vacancy_detail', pk=pk)
    else:
        form = ApplicationForm()
    
    return render(request, 'main_app/vacancy_detail.html', {
        'vacancy': vacancy,
        'form': form,
    })


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    vacancies = company.vacancy_set.filter(is_active=True)
    return render(request, 'main_app/company_detail.html', {
        'company': company,
        'vacancies': vacancies,
    })


@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'main_app/profile.html', {'profile': profile})


@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'main_app/my_applications.html', {'applications': applications})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role='applicant')
            login(request, user)
            messages.success(request, '✅ Registration successful!')
            return redirect('main_app:home')
    else:
        form = UserRegisterForm()
    return render(request, 'main_app/registration/register.html', {'form': form})