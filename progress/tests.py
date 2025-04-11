from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from .models import ProgressEntry
import datetime

class ProgressEntryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        ProgressEntry.objects.create(
            user=self.user,
            date=datetime.date.today(),
            weight=75.5,
            body_fat=15.0,
            muscle_mass=35.0
        )

    def test_export_progress_csv(self):
        url = reverse("progress-export")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("Peso (kg)", response.content.decode("utf-8"))
