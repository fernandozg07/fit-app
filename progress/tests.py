from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from progress.models import ProgressEntry

class ProgressTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='progressuser@example.com',
            password='teste123',
            weight=80,
            height=180,
            fitness_goal='perda de peso'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = '/progress/'

    def test_create_progress_entry(self):
        data = {
            "date": "2025-04-06",
            "weight": 78.5,
            "body_fat": 18.2,
            "muscle_mass": 39.0
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProgressEntry.objects.count(), 1)
        self.assertEqual(ProgressEntry.objects.first().weight, 78.5)

    def test_list_progress_entries(self):
        ProgressEntry.objects.create(
            user=self.user, date="2025-04-01", weight=80.0
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filter_progress_by_date(self):
        ProgressEntry.objects.create(
            user=self.user, date="2025-04-01", weight=80.0
        )
        ProgressEntry.objects.create(
            user=self.user, date="2025-04-06", weight=78.5
        )
        response = self.client.get(self.url + '?start_date=2025-04-05')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['date'], "2025-04-06")
