from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="clinic/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),


    # Pacientët normal
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/<int:pk>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:pk>/histories/add/", views.add_history, name="add_history"),

    # Pacientët ORTO
    path("patients/orto/", views.orto_patient_list, name="orto_patient_list"),
    path("patients/orto/<int:pk>/", views.orto_patient_detail, name="orto_patient_detail"),
    path("patients/orto/<int:pk>/histories/add/", views.add_orto_history, name="add_orto_history"),
    path("history/<int:pk>/edit/", views.edit_history, name="edit_history"),
    path("history/<int:pk>/delete/", views.delete_history, name="delete_history"),
    path("reports/", views.reports, name="reports"),
    path("patients/add/", views.add_patient, name="add_patient"),
    path("shpenzime/", views.shpenzime_list, name="shpenzime_list"),
    path("shpenzime/add/", views.shpenzime_add, name="shpenzime_add"),
    path("shpenzime/<int:pk>/delete/", views.shpenzime_delete, name="shpenzime_delete"),
    path("appointments/", views.appointments_calendar, name="appointments_calendar"),
    path("appointments/events/", views.appointments_events, name="appointments_events"),
    path("appointments/create/", views.appointments_create, name="appointments_create"),
    path("appointments/update/<int:pk>/", views.appointments_update, name="appointments_update"),
    path("appointments/delete/<int:pk>/", views.appointments_delete, name="appointments_delete"),
    path("history/<int:pk>/", views.history_detail, name="history_detail"),
    path("patients/<int:pk>/payments/add/", views.add_payment, name="add_payment"),
    path("patients/<int:pk>/agreements/new/", views.agreement_create, name="agreement_create"),
    path("agreements/<int:agreement_id>/close/", views.agreement_close, name="agreement_close"),
    path("reports/new/", views.reports_new, name="reports_new"),
    path("patients/<int:pk>/upload-document/", views.upload_document, name="upload_document"),
    path("documents/<int:pk>/delete/", views.delete_patient_document, name="delete_patient_document"),
    path("checkout/", views.checkout, name="checkout"),
    path("patients/search/", views.search_patients, name="search_patients"),








]
