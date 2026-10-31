from django.db import models


class Doctor(models.Model):
    full_name = models.CharField(max_length=120)
    specialty = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.full_name} ({self.specialty})"


class Patient(models.Model):
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    scheduled_at = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    visit_notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            # Database-level safety net: a doctor can't have two active
            # appointments at the same time.
            models.UniqueConstraint(
                fields=["doctor", "scheduled_at"],
                condition=~models.Q(status="cancelled"),
                name="unique_active_slot_per_doctor",
            )
        ]

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.scheduled_at}"
