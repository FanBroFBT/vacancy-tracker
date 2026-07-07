from django.contrib import admin
from .models import Category, Company, Vacancy, Application

admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Vacancy)
admin.site.register(Application)