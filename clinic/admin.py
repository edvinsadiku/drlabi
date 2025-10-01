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


