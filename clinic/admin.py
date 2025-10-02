from django.contrib import admin
from . import models

@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")
    search_fields = ("emri_mbiemri", "telefoni", "emaili")
    list_filter = ("created_at",)

@admin.register(models.Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("diagnoza", "trajtimi", "doctor")

@admin.register(models.HistoryOrtodentics)
class HistoryOrtoAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor")
    list_filter = ("doctor",)
    search_fields = ("diagnoza", "trajtimi", "doctor")

@admin.register(models.PatienOrtodentics)
class PatienOrtodenticsAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")

@admin.register(models.Shpenzimet)
class ShpenzimetAdmin(admin.ModelAdmin):
    list_display = ("id", "shpenzimi", "muaji", "vlera", "paguar")


# clinic/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol", {
            "classes": ("wide",),
            "fields": ("role",),
        }),
    )

    list_display = ("username", "email", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("role", "is_active", "is_staff")
