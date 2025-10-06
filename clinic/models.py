from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("worker", "Punëtor"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="worker")

    def is_admin(self):
        return self.role == "admin"

    def is_worker(self):
        return self.role == "worker"


class Patient(models.Model):
    id = models.BigAutoField(primary_key=True)
    emri_mbiemri = models.CharField(max_length=191, null=True, blank=True)
    data_e_lindjes = models.CharField(max_length=191, null=True, blank=True)
    adresa = models.CharField(max_length=191, null=True, blank=True)
    leternjoftimi = models.CharField(max_length=50, null=True, blank=True)
    telefoni = models.CharField(max_length=191, null=True, blank=True)
    emaili = models.CharField(max_length=191, null=True, blank=True)
    pytja1 = models.CharField(max_length=191, null=True, blank=True)
    pytja2 = models.CharField(max_length=191, null=True, blank=True)
    pytja3 = models.CharField(max_length=191, null=True, blank=True)
    pytja4 = models.CharField(max_length=191, null=True, blank=True)
    pytja5 = models.CharField(max_length=191, null=True, blank=True)
    pytja6 = models.CharField(max_length=191, null=True, blank=True)
    pytja7 = models.CharField(max_length=191, null=True, blank=True)
    pytja8 = models.CharField(max_length=191, null=True, blank=True)
    pytja9 = models.CharField(max_length=191, null=True, blank=True)
    pytja10 = models.CharField(max_length=191, null=True, blank=True)
    pytja11 = models.CharField(max_length=191, null=True, blank=True)
    pytja12 = models.CharField(max_length=191, null=True, blank=True)
    pytja13 = models.CharField(max_length=191, null=True, blank=True)
    pytja14 = models.CharField(max_length=191, null=True, blank=True)
    pytja15 = models.CharField(max_length=191, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "patients"
        verbose_name = "Pacientet"
        verbose_name_plural = "Pacientet"

    def __str__(self):
        return self.emri_mbiemri or f"Patient #{self.pk}"


class Historia(models.Model):
    id = models.AutoField(primary_key=True)
    emri_i_pacientit = models.CharField(max_length=191, null=True, blank=True)
    data = models.CharField(max_length=191, null=True, blank=True)
    dhembi = models.CharField(max_length=191, null=True, blank=True)
    diagnoza = models.CharField(max_length=191, null=True, blank=True)
    trajtimi = models.CharField(max_length=3000, null=True, blank=True)
    vlera = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    paguar = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    borgji = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    verejtje = models.CharField(max_length=191, null=True, blank=True)
    pasqyra_e_dhembit = models.CharField(max_length=191, null=True, blank=True)
    patient = models.ForeignKey(
        "Patient", models.DO_NOTHING, db_column="id_pacienti", related_name="historias"
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    doctor = models.CharField(max_length=191, null=True, blank=True)
    punim_protetikor = models.TextField(null=True, blank=True)
    tekniku = models.CharField(max_length=191, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "historias"
        verbose_name = "Historia(Arkiva)"
        verbose_name_plural = "Historia(Arkiva)"

    def __str__(self):
        return f"{self.data or ''} – {self.diagnoza or 'Pa diagnozë'}"


class HistoryOrtodentics(models.Model):
    id = models.AutoField(primary_key=True)
    emri_i_pacientit = models.CharField(max_length=191, null=True, blank=True)
    data = models.CharField(max_length=191, null=True, blank=True)
    dhembi = models.CharField(max_length=191, null=True, blank=True)
    diagnoza = models.CharField(max_length=191, null=True, blank=True)
    trajtimi = models.CharField(max_length=191, null=True, blank=True)
    vlera = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    paguar = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    borgji = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    verejtje = models.CharField(max_length=191, null=True, blank=True)
    doctor = models.CharField(max_length=191, null=True, blank=True)
    punim_protetikor = models.TextField(null=True, blank=True)
    tekniku = models.CharField(max_length=191, null=True, blank=True)
    patient = models.ForeignKey(
        "PatienOrtodentics",
        models.DO_NOTHING,
        db_column="id_pacienti",
        related_name="ortho_histories",
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "history_ortodentics"
        verbose_name = "Orto Histori(Arkiva)"
        verbose_name_plural = "Orto Histori(Arkiva)"


class PatienOrtodentics(models.Model):
    id = models.AutoField(primary_key=True)
    emri_mbiemri = models.CharField(max_length=191, null=True, blank=True)
    data_e_lindjes = models.CharField(max_length=191, null=True, blank=True)
    adresa = models.CharField(max_length=191, null=True, blank=True)
    telefoni = models.CharField(max_length=191, null=True, blank=True)
    emaili = models.CharField(max_length=191, null=True, blank=True)
    pytja1 = models.CharField(max_length=191, null=True, blank=True)
    pytja2 = models.CharField(max_length=191, null=True, blank=True)
    pytja3 = models.CharField(max_length=191, null=True, blank=True)
    pytja4 = models.CharField(max_length=191, null=True, blank=True)
    pytja5 = models.CharField(max_length=191, null=True, blank=True)
    pytja6 = models.CharField(max_length=191, null=True, blank=True)
    pytja7 = models.CharField(max_length=191, null=True, blank=True)
    pytja8 = models.CharField(max_length=191, null=True, blank=True)
    pytja9 = models.CharField(max_length=191, null=True, blank=True)
    pytja10 = models.CharField(max_length=191, null=True, blank=True)
    pytja11 = models.CharField(max_length=191, null=True, blank=True)
    pytja12 = models.CharField(max_length=191, null=True, blank=True)
    pytja13 = models.CharField(max_length=191, null=True, blank=True)
    pytja14 = models.CharField(max_length=191, null=True, blank=True)
    pytja15 = models.CharField(max_length=191, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "patien_ortodentics"
        verbose_name = "Pacientet orto(Arkiva)"
        verbose_name_plural = "Pacientet orto(Arkiva)"

    def __str__(self):
        return self.emri_mbiemri or f"Orto Patient #{self.pk}"


class Shpenzimet(models.Model):
    id = models.AutoField(primary_key=True)
    shpenzimi = models.CharField(max_length=191, null=True, blank=True)
    muaji = models.DateField(null=True, blank=True)
    vlera = models.IntegerField(null=True, blank=True)
    paguar = models.BooleanField(null=True, blank=True)
    pershkrimi = models.CharField(max_length=191, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "shpenzimets"
        verbose_name = "Shpenzimet"
        verbose_name_plural = "Shpenzimet"

    def __str__(self):
        return self.shpenzimi or f"Shpenzim #{self.pk}"


from django.db import models
from django.utils.timezone import now


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Planifikuar"),
        ("completed", "Përfunduar"),
        ("cancelled", "Anuluar"),
    ]

    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        db_column="patient_id",  
        related_name="appointments",
    )
    doctor = models.CharField(
        max_length=100, choices=[("Dr. Labi", "Dr. Labi"), ("Dr. Linda", "Dr. Linda")]
    )
    title = models.CharField(max_length=191, help_text="Shërbimi ose arsyeja e vizitës")
    start = models.DateTimeField(default=now)
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-start"]

    def __str__(self):
        return f"{self.patient.emri_mbiemri or 'Pa emër'} – {self.title} ({self.start:%Y-%m-%d %H:%M})"


from django.conf import settings


class PatientDocument(models.Model):
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        db_column="patient_id",
        related_name="documents",
    )
    file = models.FileField(upload_to="patient_documents/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_documents"
        managed = False
        verbose_name = "Dokumentet"
        verbose_name_plural = "Dokumentet"

    def __str__(self):
        return f"{self.patient.emri_mbiemri} - {self.file.name}"


class Agreement(models.Model):
    STATUS = [
        ("active", "Aktive"),
        ("closed", "Mbyllur"),
        ("cancelled", "Anuluar"),
    ]

    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="agreements",
        db_constraint=False,
        db_column="patient_id",
    )
    title = models.CharField(max_length=191, default="Marrëveshje trajtimi")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    notes = models.TextField(null=True, blank=True)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    doctor = models.CharField(
        max_length=191,
        choices=[("Dr. Labi", "Dr. Labi"), ("Dr. Linda", "Dr. Linda")],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_agreements",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_agreements",
    )

    class Meta:
        db_table = "lp_agreements"  # tabela e re
        ordering = ["-created_at"]
        managed = False
        verbose_name = "Marreveshjet"
        verbose_name_plural = "Marreveshjet"


    def __str__(self):
        return f"{self.patient.emri_mbiemri or 'Pacient'} – {self.title} ({self.total_amount}€)"

    @property
    def paid_amount(self) -> Decimal:
        agg = self.payments.aggregate(s=models.Sum("amount"))
        return agg["s"] or Decimal("0")

    @property
    def balance(self) -> Decimal:
        return (self.total_amount or Decimal("0")) - self.paid_amount


class CareHistory(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="care_histories",
        db_constraint=False,
        db_column="patient_id",
    )
    date = models.DateField(default=now)
    tooth = models.CharField(max_length=50, null=True, blank=True)
    diagnosis = models.CharField(max_length=191, null=True, blank=True)
    treatment = models.TextField(null=True, blank=True)

    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    doctor = models.CharField(max_length=191, null=True, blank=True)

    agreement = models.ForeignKey(
        Agreement,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="histories",
    )
    included_in_agreement = models.BooleanField(default=False)

    legacy_historia_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_care_histories",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_care_histories",
    )

    class Meta:
        db_table = "lp_care_histories"
        ordering = ["-date", "-id"]
        managed = False
        verbose_name = "Historia"
        verbose_name_plural = "Historia"

    

    def __str__(self):
        return (
            f"{self.patient.emri_mbiemri or 'Pacient'} – {self.diagnosis or 'Histori'}"
        )


class Payment(models.Model):
    METHOD = [
        ("cash", "Cash"),
        ("card", "Kartelë"),
        ("transfer", "Transfer"),
        ("other", "Tjetër"),
    ]

    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="payments",
        db_constraint=False,
        db_column="patient_id",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD, default="cash")
    date = models.DateTimeField(default=now)
    notes = models.CharField(max_length=255, null=True, blank=True)

    history = models.ForeignKey(
        CareHistory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payments",
    )
    agreement = models.ForeignKey(
        Agreement,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payments",
    )

    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_payments",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_payments",
    )

    class Meta:
        db_table = "lp_payments"
        ordering = ["-date", "-id"]
        managed = False
        verbose_name = "Pagesat"
        verbose_name_plural = "Pagesat"


    def __str__(self):
        t = "histori" if self.history_id else "marrëveshje"
        return f"{self.patient.emri_mbiemri or 'Pacient'} – {self.amount}€ ({t})"
