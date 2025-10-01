from django.db import models


class Patient(models.Model):
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
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

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
    patient = models.ForeignKey('Patient', models.DO_NOTHING, db_column='id_pacienti', related_name='historias')
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    doctor = models.CharField(max_length=191, null=True, blank=True)
    punim_protetikor = models.TextField(null=True, blank=True)
    tekniku = models.CharField(max_length=191, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'historias'
        verbose_name = 'Historia'
        verbose_name_plural = 'Historias'

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
        'PatienOrtodentics',
        models.DO_NOTHING,
        db_column='id_pacienti',
        related_name='ortho_histories'
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'history_ortodentics'
        verbose_name = 'Ortodentics History'
        verbose_name_plural = 'Ortodentics Histories'


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
        db_table = 'patien_ortodentics'
        verbose_name = 'Patient (Ortodentics)'
        verbose_name_plural = 'Patients (Ortodentics)'

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
        db_table = 'shpenzimets'
        verbose_name = 'Shpenzim'
        verbose_name_plural = 'Shpenzime'

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
        db_column="patient_id",          # 🔑 lidhja e saktë me kolonën ekzistuese
        related_name="appointments",
        
    )
    doctor = models.CharField(
        max_length=100,
        choices=[("Dr. Labi", "Dr. Labi"), ("Dr. Linda", "Dr. Linda")]
    )
    title = models.CharField(
        max_length=191,
        help_text="Shërbimi ose arsyeja e vizitës"
    )
    start = models.DateTimeField(default=now)
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled"
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        managed = False 
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
        related_name="documents"
    )
    file = models.FileField(upload_to="patient_documents/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="uploaded_documents"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_documents"

    def __str__(self):
        return f"{self.patient.emri_mbiemri} - {self.file.name}"
