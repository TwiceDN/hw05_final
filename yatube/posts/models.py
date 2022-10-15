from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q
from django.db.models import CheckConstraint, UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста",
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = 'Текст поста'
        verbose_name_plural = "Текст постов"

    def __str__(self) -> str:
        return self.text


class Comment(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        max_length=500,
        verbose_name='Текст',
        help_text='Текст нового комментария'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Подписка'
        verbose_name_plural = "Подписки"
        UniqueConstraint(fields=['author', 'user'], name='unique_user')
        CheckConstraint(name='not_same', check=~Q(follower=F('following')))
