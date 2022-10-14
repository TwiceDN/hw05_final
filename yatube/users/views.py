from django.views.generic import CreateView

# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy
from django.core.mail import send_mail
# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PsswordResetView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_form.html'
    send_mail(
        'Тема письма',
        'Текст письма.',
        'from@example.com',  # Это поле "От кого"
        ['to@example.com'],  # Это поле "Кому" (можно указать список адресов)
        fail_silently=False,  # Сообщать об ошибках («молчать ли об ошибках?»)
    )


class PsswordChangeView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_change_form.html'


class PsswordChangeDoneView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_change_done.html'


class PsswordResetDoneView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_done.html'


class PsswordResetConfirmView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_confirm.html'


class PsswordResetCompleteView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/password_reset_complete.html'
