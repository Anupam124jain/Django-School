from django.contrib import admin
from .models import *

# Register your models here.
models = [Subject,Quiz,Question,Answer,Student,TakenQuiz,StudentAnswer]
admin.site.register(models)