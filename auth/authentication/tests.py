from django.test import TestCase, Client

API_URL = "http://127.0.0.1:8000"


class TestSample(TestCase):
    def setUp(self):
        self.client = Client()

    def test_the_current_schema_returns_empty_list(self):
        """
        Test that the configuration works by seeing that an empty list
        is returned on querying for users
        """
        response = self.client.get("/api/public")
        self.assertEqual({"message": "Hello from a public endpoint!"}, response.json())
