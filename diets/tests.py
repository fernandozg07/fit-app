from django.test import TestCase
from django.contrib.auth import get_user_model
from diets.models import Diet
from datetime import date

User = get_user_model()

class DietModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="securepassword"
        )
        self.user.objetivo = "Ganhar massa"
        self.user.data_nascimento = "2000-01-01"
        self.user.peso = 70
        self.user.altura = 1.75
        self.user.save()

    def test_create_diet_entry(self):
        diet = Diet.objects.create(
            user=self.user,
            meal='lunch',
            calories=600,
            protein=35,
            carbs=70,
            fat=20
        )
        self.assertEqual(str(diet), f"Lunch - {self.user.email} ({diet.date})")
