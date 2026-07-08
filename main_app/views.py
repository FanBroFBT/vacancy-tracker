from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Vacancy, Company, Application, Profile
from .forms import UserRegisterForm, ApplicationForm, VacancyForm, CompanyForm, ProfileForm


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
    form = ApplicationForm()
    return render(request, 'main_app/vacancy_detail.html', {
        'vacancy': vacancy,
        'form': form,
    })


@login_required
def vacancy_applications(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.user.profile.role != 'employer':
        messages.error(request, '❌ Access denied. Only employers can view applications.')
        return redirect('main_app:home')

    if request.user != vacancy.company.owner:
        messages.error(request, '❌ You are not the owner of this vacancy.')
        return redirect('main_app:vacancy_detail', pk=pk)

    applications = Application.objects.filter(vacancy=vacancy).order_by('-applied_at')

    return render(request, 'main_app/vacancy_applications.html', {
        'vacancy': vacancy,
        'applications': applications,
    })


@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    vacancy = application.vacancy

    if request.user.profile.role != 'employer':
        messages.error(request, '❌ Access denied.')
        return redirect('main_app:home')

    if request.user != vacancy.company.owner:
        messages.error(request, '❌ You are not the owner of this vacancy.')
        return redirect('main_app:vacancy_detail', pk=vacancy.pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['accepted', 'rejected']:
            application.status = status
            application.save()
            messages.success(request, f'✅ Application {status}!')
        else:
            messages.error(request, '❌ Invalid status.')

    return redirect('main_app:vacancy_applications', pk=vacancy.pk)


@login_required
def create_vacancy(request):
    if request.user.profile.role != 'employer':
        messages.error(request, 'You are not employer')
        return redirect('main_app:home')

    if not hasattr(request.user, 'company'):
        messages.error(request, 'Сначала создайте компанию')
        return redirect('main_app:create_company')

    if request.method == 'GET':
        form = VacancyForm()
        return render(request, 'main_app/create_vacancy.html', {'form': form})
    elif request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.company = request.user.company
            vacancy.save()
            messages.success(request, 'Succesfully created!')
            return redirect('main_app:vacancy_detail', pk=vacancy.pk)
        else:
            return render(request, 'main_app/create_vacancy.html', {'form': form})


@login_required
def create_company(request):
    if request.user.profile.role != 'employer':
        messages.error(request, 'You are not employer')
        return redirect('main_app:home')

    if hasattr(request.user, 'company'):
        return redirect('main_app:company_edit')

    if request.method == 'GET':
        form = CompanyForm()
        return render(request, 'main_app/create_company.html', {'form': form})
    elif request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, 'Succesfully created!')
            return redirect('main_app:company_detail', pk=company.pk)
        else:
            return render(request, 'main_app/create_company.html', {'form': form})


@login_required
def apply_to_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.user.profile.role != 'applicant':
        messages.error(request, '❌ Only applicants can apply to vacancies!')
        return redirect('main_app:vacancy_detail', pk=pk)

    existing_application = Application.objects.filter(
        vacancy=vacancy,
        applicant=request.user
    ).exists()

    if existing_application:
        messages.warning(request, '⚠️ You already applied to this vacancy!')
        return redirect('main_app:vacancy_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.applicant = request.user
            application.save()
            messages.success(request, '✅ Application submitted successfully!')
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
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'applicant'}
    )
    if created:
        messages.info(request, '✅ Profile was automatically created for you!')
    
    company = Company.objects.filter(owner=request.user).first()
    return render(request, 'main_app/profile.html', {'profile': profile, 'company': company})

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    company = Company.objects.filter(owner=profile.user).first()
    return render(request, 'main_app/profile_detail.html', {
        'profile': profile,
        'company': company,
    })

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'GET':
        form = ProfileForm(instance=profile)
        return render(request, 'main_app/profile_edit.html', {'form': form})
    elif request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated!')
            return redirect('main_app:profile')
        else:
            return render(request, 'main_app/profile_edit.html', {'form': form})


@login_required
def company_edit(request):
    if request.user.profile.role != 'employer':
        messages.error(request, 'You are not employer')
        return redirect('main_app:home')

    company = get_object_or_404(Company, owner=request.user)

    if request.method == 'GET':
        form = CompanyForm(instance=company)
        return render(request, 'main_app/company_edit.html', {'form': form})
    elif request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Company updated!')
            return redirect('main_app:company_detail', pk=company.pk)
        else:
            return render(request, 'main_app/company_edit.html', {'form': form})


@login_required
def my_applications(request):
    if request.user.profile.role != 'applicant':
        messages.error(request, '❌ Only applicants can view applications!')
        return redirect('main_app:home')

    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'main_app/my_applications.html', {'applications': applications})


@login_required
def my_vacancies(request):
    if request.user.profile.role != 'employer':
        messages.error(request, '❌ Only employers can view their vacancies.')
        return redirect('main_app:home')

    if not hasattr(request.user, 'company'):
        messages.warning(request, '⚠️ You haven\'t created a company yet.')
        return redirect('main_app:create_company')

    vacancies = Vacancy.objects.filter(company=request.user.company).order_by('-created_at')

    for vacancy in vacancies:
        vacancy.applications_count = Application.objects.filter(vacancy=vacancy).count()
        vacancy.new_applications_count = Application.objects.filter(vacancy=vacancy, status='send').count()

    return render(request, 'main_app/my_vacancies.html', {'vacancies': vacancies})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            messages.success(request, '✅ Registration successful! Welcome to JobTracker!')
            return redirect('main_app:home')
    else:
        form = UserRegisterForm()
    return render(request, 'main_app/registration/register.html', {'form': form})