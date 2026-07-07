from django.contrib import admin
from .models import Profile, Company, Vacancy, Application

admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Vacancy)
admin.site.register(Application)