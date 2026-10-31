from rest_framework import viewsets

from .models import Appointment, Doctor, Patient
from .serializers import AppointmentSerializer, DoctorSerializer, PatientSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.order_by("id")
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.order_by("id")
    serializer_class = PatientSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.order_by("scheduled_at")
    serializer_class = AppointmentSerializer
