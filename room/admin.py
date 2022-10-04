from django.contrib import admin
from .models import Room


# Register your models here.
@admin.register(Room)
class AdminModel(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name'],}
