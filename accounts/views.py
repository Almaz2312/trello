import django.contrib.auth.backends
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse
from django.views import View
from django.views import generic

from accounts.forms import CustomUserCreationForm, CustomPasswordResetForm
from accounts.services import send_message


User = get_user_model()


class Dashboard(generic.TemplateView):
    template_name = 'user/dashboard.html'


class Register(View):
    def get(self, request):
        return render(request, 'user/register.html', context={'form': CustomUserCreationForm})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.create_activation_code()
            user.is_active = False
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            send_message(user)
            print(user.activation_code)
            return redirect('dashboard')


class ActivateAccount(View):
    def get(self, request, activation_code):
        user = User.objects.get(activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return redirect(reverse('login'))


class CustomSetPasswordView(PasswordResetConfirmView):
    form_class = CustomPasswordResetForm
