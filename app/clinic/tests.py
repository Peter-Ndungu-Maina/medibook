from rest_framework import status
from rest_framework.test import APITestCase

from .models import Doctor, Patient


class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(full_name="Dr. Test", specialty="GP")
        self.patient = Patient.objects.create(full_name="Jane Test")
        self.payload = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "scheduled_at": "2026-11-05T09:00:00Z",
            "reason": "Check-up",
        }

    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "up")

    def test_create_appointment(self):
        response = self.client.post("/api/appointments/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_double_booking_is_rejected(self):
        self.client.post("/api/appointments/", self.payload, format="json")
        response = self.client.post("/api/appointments/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelled_slot_can_be_rebooked(self):
        first = self.client.post("/api/appointments/", self.payload, format="json")
        self.client.patch(
            f"/api/appointments/{first.json()['id']}/", {"status": "cancelled"}, format="json"
        )
        again = self.client.post("/api/appointments/", self.payload, format="json")
        self.assertEqual(again.status_code, status.HTTP_200_OK)
