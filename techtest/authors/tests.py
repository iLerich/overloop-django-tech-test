import json

from django.test import TestCase
from django.urls import reverse

from techtest.authors.models import Author


class AuthorListViewsTestCase(TestCase):
    def setUp(self):
        self.url = reverse("authors-list")
        self.arthour1 = Author.objects.create(
            first_name="First 1", last_name="Last 1")
        self.arthour2 = Author.objects.create(
            first_name="First 2", last_name="Last 2")

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.arthour1.id,
                    "first_name": "First 1",
                    "last_name": "Last 1",
                },
                {
                    "id": self.arthour2.id,
                    "first_name": "First 2",
                    "last_name": "Last 2",
                },
            ]
        )

    def test_creates_new_author(self):
        payload = {
            "first_name": "First 1",
            "last_name": "Last 1",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        author = Author.objects.last()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(author)
        self.assertDictEqual(
            response.json(),
            {
                "id": author.id,
                "first_name": "First 1",
                "last_name": "Last 1",
            }
        )


class AuthorViewTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="First", last_name="Last")
        self.url = reverse("author", kwargs={"author_id": self.author.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.author.id,
                "first_name": "First",
                "last_name": "Last",
            },
        )

    def test_updates_author(self):
        payload = {
            "id": self.author.id,
            "first_name": "First 2",
            "last_name": "Last 2",
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        author = Author.objects.filter(id=self.author.id).first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(author)
        self.assertEqual(Author.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": author.id,
                "first_name": "First 2",
                "last_name": "Last 2",
            },
            response.json(),
        )

    def test_removes_author(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 0)
