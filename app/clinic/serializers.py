from rest_framework import serializers

from .models import Appointment, Doctor, Patient


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

    def validate(self, attrs):
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        when = attrs.get("scheduled_at", getattr(self.instance, "scheduled_at", None))

        clash = Appointment.objects.filter(doctor=doctor, scheduled_at=when).exclude(
            status=Appointment.Status.CANCELLED
        )
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError("This doctor is already booked at that time.")
        return attrs
