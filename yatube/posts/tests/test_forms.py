from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User
from posts.forms import PostForm


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Test_User')
        cls.group = Group.objects.create(title='группа0', slug='test_slug0',
                                         description='проверка описания0')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.form = PostForm()

    def test_create_post(self):
        posts_count = Post.objects.count()
        post = Post.objects.first()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.title, 'группа0')

    def test_edit_post(self):
        old_post = self.post
        form_data = {
            'text': 'Новый тестовый текст',
        }
        self.authorized_client.post(
            reverse('posts:edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=1)
        self.assertNotEqual(old_post.text, new_post.text)
