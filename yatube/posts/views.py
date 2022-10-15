from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings

from .models import Post, Group, Comment, Follow, User
from .forms import PostForm, CommentForm
from .utils import paginator_def


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    # Отдаем в словаре контекста
    context = {
        'page_obj': paginator_def(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    template = 'posts/group_list.html'
    context = {'group': group, 'page_obj': paginator_def(request, posts)}
    return render(request, template, context)


def profile(request, username, following=False):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    template = 'posts/profile.html'
    following_button = False
    following = request.user.is_authenticated and Follow.objects.filter(
        author=author,
        user=request.user).exists()
    following_button = True
    context = {
        'page_obj': paginator_def(request, posts),
        'author': author,
        'following': following,
        'following_button': following_button}
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = str(post.text)[:settings.LIMIT_TEXT]
    number_of_posts = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'title': title,
        'number_of_posts': number_of_posts,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Все посты ваших подписок'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.NUMBER_POST)
    page_number = request.GET.get('page_obj')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following_exists = Follow.objects.filter(
        author=author,
        user=request.user).exists()
    user_author = request.user != author
    if user_author and (request.user != author and not following_exists):
        Follow.objects.create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
