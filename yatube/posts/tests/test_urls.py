from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="Test_User",)

        cls.group = Group.objects.create(
            id="10",
            title="группа",
            slug="one_group",
            description="проверка описания",
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.get(username="Test_User"),
            group=Group.objects.get(title="группа"),
        )

        cls.access_urls = {
            '/': 'all',
            f'/posts/{cls.post.pk}/edit/': 'author',
            '/create/': 'authorized'
        }

        cls.another_dict = {
            '/': 'posts/index.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }

        cls.post_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.public_urls = (
            ('/', 'index.html'),
            (f'/group/{cls.group.slug}/', 'group.html'),
            (f'/profile/{cls.user.username}/', 'profile.html'),
            (cls.post_url, 'post.html'),
        )
        cls.private_urls = (
            ('/create/', 'create_post.html'),
            (cls.post_edit_url, 'create_post.html')
        )
        cls.templates_url_names = {
            '/group/one_group/': 'posts/group_list.html',
            '/profile/Test_User/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.get(username="Test_User")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем доступ для авторизованного пользователя и автора
    def test_private_pages(self):
        for data in self.private_urls:
            response = self.authorized_client.get(data[0])
            self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступ для НЕ авторизованного пользователя и автора
    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/admin/',
            '/create/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    # Проверяем статус 404 для авторизованного пользователя
    def test_task_list_url_redirect_anonymous(self):
        """Страница /kdgjkaklsadgajk/ не существует."""
        response = self.authorized_client.get('/kdgjkaklsadgajk/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404_on_not_existing_page(self):
        response = self.authorized_client.get(
            '/not_exists/'
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
