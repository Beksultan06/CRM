import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db

@pytest.fixture
def student(django_user_model):
    return django_user_model.objects.create_user(username="stud1", password="pass", role="Ученик")

@pytest.fixture
def api_client():
    return APIClient()


def test_lesson_endpoint_returns_only_students_lessons(student, api_client):
    api_client.login(username="stud1", password="pass")
    url = reverse("student-lessons-list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)