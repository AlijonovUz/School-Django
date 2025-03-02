from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import *
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from django.views import View
from .decoratos import *
from .mixins import *
from .forms import *


class Index(ListView):
    model = Student

    template_name = 'manager/index.html'
    context_object_name = 'students'
    paginate_by = 3

    extra_context = {
        'current_year': datetime.now().year
    }

    ordering = ['name']

    def get_queryset(self):
        return Student.objects.select_related('course').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['courses'] = Course.objects.all()
        return context


class CourseDetail(LoginRequiredMixin, Index):

    def get_queryset(self):
        return Student.objects.filter(course_id=self.kwargs.get('pk')).select_related('course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs.get('pk'))
        context['courses'] = [course]
        return context


class Search(LoginRequiredMixin, View):

    def get(self, request):
        query = request.GET.get('q')
        if query:
            results = Course.objects.filter(title__icontains=query)

            context = {
                'query': query,
                'results': results
            }

            return render(request, 'search.html', context)
        return redirect('index')


class StudentDetail(LoginRequiredMixin, DetailView):
    model = Student
    extra_context = {
        'current_year': datetime.now().year
    }

    def get_queryset(self):
        return Student.objects.select_related('course').all()


class AddCourse(PermissionRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    permission_required = 'manager.add_course'

    extra_context = {
        'current_year': datetime.now().year
    }

    def handle_no_permission(self):
        return redirect('not_found')

    def form_valid(self, form):
        messages.success(self.request, "Ma'lumot muvaffaqiyatli saqlandi.")
        return super().form_valid(form)


class UpdateCourse(PermissionRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    permission_required = 'manager.change_course'

    extra_context = {
        'current_year': datetime.now().year
    }

    def handle_no_permission(self):
        return redirect('not_found')

    def form_valid(self, form):
        messages.success(self.request, "Ma'lumot muvaffaqiyatli o'zgartirildi.")
        return super().form_valid(form)


class DeleteCourse(PermissionRequiredMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('index')
    permission_required = 'manager.delete_course'

    def handle_no_permission(self):
        return redirect('not_found')

    def form_valid(self, form):
        messages.success(self.request, "Ma'lumot muvaffaqiyatli o'chirildi.")
        return super().form_valid(form)


class Register(LoginNoRequired, CreateView):
    model = MyUser
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'
    login_url = reverse_lazy('index')

    def form_valid(self, form):
        messages.success(self.request, "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!")
        return super().form_valid(form)


class Login(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Siz muvaffaqiyatli tizimga kirdingiz!")
        return super().form_valid(form)


class Logout(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(self.request, "Siz muvaffaqiyatli tizimdan chiqdingiz!")
        return redirect('login')


class SendEmail(LoginRequiredMixin, StaffRequired, View):

    def get(self, request):
        form = EmailForm()

        context = {
            'form': form,
            'current_year': datetime.now().year
        }

        return render(request, 'sendEmail.html', context)

    def post(self, request):
        form = EmailForm(data=request.POST)
        if form.is_valid():
            users = MyUser.objects.all()
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            for user in users:
                send_mail(
                    subject,
                    message,
                    "Najot Ta'lim <alijonov.me@gmail.com>",
                    [user.email],
                    fail_silently=False
                )

            messages.success(request, "Xabaringiz foydalanuvchilarga muvaffaiyatli yuborildi.")
            return redirect('send_email')

        context = {
            'form': form,
            'current_year': datetime.now().year
        }

        return render(request, 'sendEmail.html', context)


class Settings(LoginRequiredMixin, View):

    def get(self, request):
        user = get_object_or_404(MyUser, username=request.user.username)
        form = SettingsForm(instance=user)
        password_form = PasswordForm(user=request.user)

        context = {
            'forms': form,
            'changePassword': password_form,
            'current_year': datetime.now().year
        }

        return render(request, 'settings.html', context)

    def post(self, request):
        user = get_object_or_404(MyUser, username=request.user.username)
        form = SettingsForm(instance=user)
        password_form = PasswordForm(user=request.user)

        if 'update_profile' in request.POST:
            form = SettingsForm(data=request.POST, files=request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Ma'lumotlar muvaffaqiyatli saqlandi.")
                return redirect('personal_data')

        elif 'change_password' in request.POST:
            password_form = PasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)

                messages.success(request, "Parol muvaffaqiyatli o'zgartirildi.")
                return redirect('change_password')
        elif 'delete_photo' in request.POST:
            if user.photo:
                user.photo = None
                user.save()

                messages.success(request, "Profil rasmingiz o'chirildi.")
            else:
                messages.error(request, "Sizda profil rasm mavjud emas!")

            return redirect('delete_photo')

        elif 'delete_account' in request.POST:
            user.delete()

            messages.success(request, "Hisobingiz muvaffaqiyatli o'chirildi.")
            return redirect('index')

        context = {
            'forms': form,
            'changePassword': password_form,
            'current_year': datetime.now().year
        }

        return render(request, 'settings.html', context)


class Profile(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MyUser
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(MyUser, username=username)
        return user

    def test_func(self):
        return self.request.user.username == self.kwargs.get('username')

    def handle_no_permission(self):
        return redirect('not_found')


class NotFound(View):

    def get(self, request):
        context = {
            'current_year': datetime.now().year
        }

        return render(request, '404.html', context, status=404)
