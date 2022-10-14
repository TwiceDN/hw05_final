from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_url_names = {
            'author': '/about/author/',
            'tech': '/about/tech/'}

    def test_about_author_url_exists_at_desired_location(self):
        response = self.guest_client.get(self.templates_url_names['author'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author_url_uses_correct_template(self):
        response = self.guest_client.get(self.templates_url_names['author'])
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_url_exists_at_desired_location(self):
        response = self.guest_client.get(self.templates_url_names['tech'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_uses_correct_template(self):
        response = self.guest_client.get(self.templates_url_names['tech'])
        self.assertTemplateUsed(response, 'about/tech.html')
