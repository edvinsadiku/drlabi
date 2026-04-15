from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Roli", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Roli", {"classes": ("wide",), "fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email")

@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")
    search_fields = ("emri_mbiemri", "telefoni", "emaili", "informata_shtese")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    class Meta:
        verbose_name = "Pacient"
        verbose_name_plural = "Pacientë"


@admin.register(models.Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor", "created_at")
    list_filter = ("doctor", "created_at")
    search_fields = ("diagnoza", "trajtimi", "doctor")
    ordering = ("-created_at",)

    class Meta:
        verbose_name = "Histori"
        verbose_name_plural = "Histori të Pacientëve"

@admin.register(models.HistoryOrtodentics)
class HistoryOrtoAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "data", "diagnoza", "vlera", "paguar", "borgji", "doctor")
    list_filter = ("doctor",)
    search_fields = ("diagnoza", "trajtimi", "doctor")
    ordering = ("-data",)

    class Meta:
        verbose_name = "Histori Ortodontike"
        verbose_name_plural = "Histori Ortodontike"


@admin.register(models.PatienOrtodentics)
class PatienOrtodenticsAdmin(admin.ModelAdmin):
    list_display = ("id", "emri_mbiemri", "telefoni", "emaili", "created_at")
    search_fields = ("emri_mbiemri", "telefoni", "emaili")
    ordering = ("-created_at",)

    class Meta:
        verbose_name = "Pacient Ortodontik"
        verbose_name_plural = "Pacientë Ortodontikë"

@admin.register(models.Shpenzimet)
class ShpenzimetAdmin(admin.ModelAdmin):
    list_display = ("id", "shpenzimi", "muaji", "vlera", "paguar")
    list_filter = ("muaji",)
    search_fields = ("shpenzimi",)
    ordering = ("-muaji",)

    class Meta:
        verbose_name = "Shpenzim"
        verbose_name_plural = "Shpenzime"

@admin.register(models.PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "file", "uploaded_by", "uploaded_at")
    list_filter = ("uploaded_at", "uploaded_by")
    search_fields = ("file",)
    ordering = ("-uploaded_at",)

    class Meta:
        verbose_name = "Dokument Pacienti"
        verbose_name_plural = "Dokumente Pacientësh"

@admin.register(models.Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "title", "total_amount", "status", "doctor", "start_date", "end_date")
    list_filter = ("status", "doctor", "start_date")
    search_fields = ("title", "notes")
    ordering = ("-start_date",)

    class Meta:
        verbose_name = "Marrëveshje"
        verbose_name_plural = "Marrëveshje"

@admin.register(models.CareHistory)
class CareHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "date", "diagnosis", "amount", "doctor", "included_in_agreement")
    list_filter = ("doctor", "date", "included_in_agreement")
    search_fields = ("diagnosis", "treatment", "doctor")
    ordering = ("-date",)

    class Meta:
        verbose_name = "Histori e Kujdesit"
        verbose_name_plural = "Histori të Kujdesit"

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "amount", "method", "doctor", "date", "agreement", "history")
    list_filter = ("method", "doctor", "date")
    search_fields = ("notes", "doctor")
    ordering = ("-date",)

    class Meta:
        verbose_name = "Pagesë"
        verbose_name_plural = "Pagesa"



@admin.register(models.Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",          # lidhja reale (shfaqet si objekti Patient)
        "patient_name",     # snapshot teksti
        "doctor",
        "prescription_date",
        "has_allergy",
        "complaint_short",
    )
    list_filter = ("doctor", "prescription_date")
    search_fields = (
        "patient__emri_mbiemri",  # kërko te pacienti
        "patient_name", "complaint", "diagnosis", "therapy", "allergy_notes",
    )
    date_hierarchy = "prescription_date"
    ordering = ("-prescription_date", "-id")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("patient", "created_by")  # më shpejt për DB të mëdha

    fieldsets = (
        ("Pacienti", {
            "fields": ("patient", "patient_name", "patient_birthdate", "patient_address")
        }),
        ("Përmbajtja e recetës", {
            "fields": ("complaint", "diagnosis", "therapy", "allergy_notes")
        }),
        ("Meta", {
            "fields": ("doctor", "prescription_date", "created_by", "created_at", "updated_at")
        }),
    )

    @admin.display(description="Alergji", boolean=True)
    def has_allergy(self, obj):
        return bool(obj.allergy_notes)

    @admin.display(description="Ankesa (shkurt)")
    def complaint_short(self, obj):
        if not obj.complaint:
            return "-"
        t = obj.complaint.strip().replace("\n", " ")
        return (t[:60] + "…") if len(t) > 60 else t


admin.site.site_header = "🦷 Paneli i Administrimit – DR Labi"
admin.site.site_title = "Administrimi i Klinikës DR Labi"
admin.site.index_title = "Menaxhimi i Pacientëve, Historive dhe Pagesave"
