from django import forms
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1',
                                            email='test1@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 1 поста',
            group=Group.objects.create(
                title='Заголовок для 1 тестовой группы',
                slug='test_slug1'))

        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name2',
                                            email='test2@mail.ru',
                                            password='test_pass',),
            text='Тестовая запись для создания 2 поста',
            group=Group.objects.create(
                title='Заголовок для 2 тестовой группы',
                slug='test_slug2'))

        cls.post_id = cls.post.id
        cls.post_comment_url = (
            'posts:add_comment',
            None,
            {'post_id': cls.post_id})
        cls.index_template = (
            'posts:index',
            'posts/index.html',
            None
        )
        cls.profile_follow_template = (
            'posts:profile_follow',
            None,
            {'username': cls.post.author.username})
        cls.templates_page_names = {

            'posts/create_post.html': reverse('posts:create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test_slug2'})
            ),
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_pages_show_correct_context(self):
        """Шаблон группы"""
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug': 'test_slug2'}))
        first_object = response.context["group"]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        self.assertEqual(group_title_0, 'Заголовок для 2 тестовой группы')
        self.assertEqual(group_slug_0, 'test_slug2')

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug1'}))
        try:
            first_object = response.context["page_obj"][0]
        except IndexError:
            print('context not found')
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Тестовая запись для создания 2 поста')

    def test_new_post_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_name2'}))
        try:
            first_object = response.context["page_obj"][0]
        except IndexError:
            print('context not found')
        post_text_0 = first_object.text
        self.assertEqual(response.context['author'].username, 'test_name2')
        self.assertEqual(post_text_0, 'Тестовая запись для создания 2 поста')

    def test_new_comment_is_created(self):
        form_data = {
            'text': 'test_text'
        }
        self.authorized_client.post(
            reverse(
                PostTests.post_comment_url[0],
                kwargs=PostTests.post_comment_url[2]
            ),
            data=form_data,
            follow=True
        )
        try:
            new_comment = get_object_or_404(Comment, text='test_text')
        except Http404:
            new_comment = None
        self.assertIsNotNone(new_comment)

    def test_index_post_is_in_cache_after_deleting(self):
        response_1 = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        )
        content_before_post_deletion = response_1.content
        post_to_delete = Post.objects.get(pk=1)
        post_to_delete.delete()
        response_2 = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        )
        content_after_post_deletion = response_2.content
        self.assertEqual(
            content_before_post_deletion,
            content_after_post_deletion)

    def test_index_post_is_not_in_content_if_cache_cleared(self):
        response_1 = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        )
        content_before_post_deletion = response_1.content
        post_to_delete = Post.objects.get(pk=1)
        post_to_delete.delete()
        cache.clear()
        response_2 = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        )
        content_after_post_deletion = response_2.content
        self.assertNotEqual(
            content_before_post_deletion,
            content_after_post_deletion)

    def test_authorized_user_can_follow(self):
        author_username = PostTests.profile_follow_template[2]['username']
        author = User.objects.get(username=author_username)
        self.authorized_client.get(
            reverse(
                PostTests.profile_follow_template[0],
                kwargs={'username': author_username})
        )
        following = Follow.objects.filter(
            author=author,
            user=self.user
        ).exists()
        self.assertTrue(following)

    def test_authorized_user_can_unfollow(self):
        author_username = PostTests.profile_follow_template[2]['username']
        author = User.objects.get(username=author_username)
        self.authorized_client.get(
            reverse(
                PostTests.profile_follow_template[0],
                kwargs={'username': author_username})
        )
        self.authorized_client.get(
            reverse(
                PostTests.profile_follow_template[0],
                kwargs={'username': author_username})
        )
        following = Follow.objects.filter(
            author=author,
            user=self.user
        ).exists()
        self.assertTrue(following)

    def test_new_posts_from_following_are_exists(self):
        author_username = PostTests.profile_follow_template[2]['username']
        author = User.objects.get(username=author_username)
        response = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        ).content
        Post.objects.create(
            text='fdfsfsdfsdfsdfsdffvdcvcx',
            author=author,
        )
        response_2 = self.authorized_client.get(
            reverse(PostTests.index_template[0])
        ).content
        self.assertEqual(response, response_2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(settings.NUMBER_POST + 3):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.list_urls = {
            reverse("posts:index") + "?page=2": "posts:index",
            reverse(
                "posts:group_list", kwargs={"slug": "test_slug2"}) + "?page=2":
                    "group",
        }

    def test_second_page_contains_three_posts(self):
        for tested_url in self.list_urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3)
