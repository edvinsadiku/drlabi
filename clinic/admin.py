from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

#CustomUser
@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol", {"classes": ("wide",), "fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("role", "is_active", "is_staff")


#Patient
@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")
    search_fields = ("emri_mbiemri", "telefoni", "emaili")
    list_filter = ("created_at",)


#Historia
@admin.register(models.Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("diagnoza", "trajtimi", "doctor")


#History Ortodentics
@admin.register(models.HistoryOrtodentics)
class HistoryOrtoAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor")
    list_filter = ("doctor",)
    search_fields = ("diagnoza", "trajtimi", "doctor")


#Patient Ortodentics
@admin.register(models.PatienOrtodentics)
class PatienOrtodenticsAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")


#Shpenzimet
@admin.register(models.Shpenzimet)
class ShpenzimetAdmin(admin.ModelAdmin):
    list_display = ("id", "shpenzimi", "muaji", "vlera", "paguar")



#Patient Documents
@admin.register(models.PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "file", "uploaded_by", "uploaded_at")
    list_filter = ("uploaded_at", "uploaded_by")
    search_fields = ("file",)


#Agreement
@admin.register(models.Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "title", "total_amount", "status", "doctor", "start_date", "end_date")
    list_filter = ("status", "doctor", "start_date")
    search_fields = ("title", "notes")


#Care History
@admin.register(models.CareHistory)
class CareHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "date", "diagnosis", "amount", "doctor", "included_in_agreement")
    list_filter = ("doctor", "date", "included_in_agreement")
    search_fields = ("diagnosis", "treatment", "doctor")


#Payments
@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "amount", "method", "date", "agreement", "history")
    list_filter = ("method", "date")
    search_fields = ("notes",)
