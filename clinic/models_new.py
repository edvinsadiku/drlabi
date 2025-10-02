from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from django.conf import settings

class Agreement(models.Model):
    STATUS = [
        ("active", "Aktive"),
        ("closed", "Mbyllur"),
        ("cancelled", "Anuluar"),
    ]

    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="agreements",db_constraint=False,db_column="patient_id")
    title = models.CharField(max_length=191, default="Marrëveshje trajtimi")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    notes = models.TextField(null=True, blank=True)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="created_agreements"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="updated_agreements"
    )

    class Meta:
        db_table = "lp_agreements"   # tabela e re
        ordering = ["-created_at"]
        managed = False

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
    """
    Historia e RE (paralele me 'historias'). Mund të lidhet opsionalisht me një marrëveshje.
    Nëse është e lidhur me marrëveshje dhe 'included_in_agreement' është True,
    atëherë s’ka nevojë të ketë çmim (ose mund të jetë 0).
    """
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="care_histories",db_constraint=False,db_column="patient_id")
    date = models.DateField(default=now)
    tooth = models.CharField(max_length=50, null=True, blank=True)
    diagnosis = models.CharField(max_length=191, null=True, blank=True)
    treatment = models.TextField(null=True, blank=True)

    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    doctor = models.CharField(max_length=191, null=True, blank=True)

    # Lidhje opsionale me marrëveshje
    agreement = models.ForeignKey(Agreement, null=True, blank=True, on_delete=models.SET_NULL, related_name="histories")
    included_in_agreement = models.BooleanField(default=False)

    # referencë opsionale te rekordi i vjetër (për audit/trace)
    legacy_historia_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="created_care_histories"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="updated_care_histories"
    )

    class Meta:
        db_table = "lp_care_histories"
        ordering = ["-date", "-id"]
        managed = False

    def __str__(self):
        return f"{self.patient.emri_mbiemri or 'Pacient'} – {self.diagnosis or 'Histori'}"


class Payment(models.Model):
    METHOD = [
        ("cash", "Cash"),
        ("card", "Kartelë"),
        ("transfer", "Transfer"),
        ("other", "Tjetër"),
    ]

    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="payments",db_constraint=False,db_column="patient_id")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD, default="cash")
    date = models.DateTimeField(default=now)
    notes = models.CharField(max_length=255, null=True, blank=True)

    # Një pagesë mund të jetë për një histori TË RE specifike...
    history = models.ForeignKey(CareHistory, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    # ... ose për një marrëveshje (akontim ose këst)
    agreement = models.ForeignKey(Agreement, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")

    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="created_payments"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="updated_payments"
    )

    class Meta:
        db_table = "lp_payments"
        ordering = ["-date", "-id"]
        managed = False

    def __str__(self):
        t = "histori" if self.history_id else "marrëveshje"
        return f"{self.patient.emri_mbiemri or 'Pacient'} – {self.amount}€ ({t})"
