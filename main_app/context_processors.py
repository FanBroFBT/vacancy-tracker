from .models import Application

def counter(request):
    if request.user.is_authenticated:
        count = Application.objects.filter(applicant=request.user).count()
        return {'count': count}
    else:
        return {'count': 0}
