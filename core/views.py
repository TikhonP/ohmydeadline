from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm, DeadlineForm
from core.models import Deadline
from django.utils import timezone
import datetime


def main_page(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            return render(request, 'main.html', )
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def loginp(request):
    if request.user.is_authenticated:
        return authed(request)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    messages.error(request, "Неактивный аккаунт")
            else:
                messages.error(request, 'Неправильный логин или пароль!')
    elif request.method == 'GET':
        form = LoginForm()
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
    return render(request, 'login.html', {'form': form})


def registerp(request):
    if request.user.is_authenticated:
        return authed(request)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['password']!=cd['password1']:
                messages.error(request, 'Пароли не совпадают! Проверьте правильность ввода паролей или придумайте новые.')
            else:
                user = authenticate(username=cd['username'], password=cd['password'])
                if not user:
                    user = form.save()
                    login(request, user)
                    return redirect('/')
                else:
                    messages.error(
                        request, 'Логин уже существует! Придумайте новый, проявите фантазию!')
    elif request.method == 'GET':
        form = RegisterForm()
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
    return render(request, 'register.html', {'form': form})


def authed(request):
    if request.method == 'GET':
        mydeadlines = Deadline.objects.filter(user=request.user).order_by("-date_deadline")
        nowtime = timezone.now()

        for i in range(len(mydeadlines)):
            mydeadlines[i].is_timeout = (mydeadlines[i].date_deadline - nowtime).total_seconds() <= 0


        deadlines_for_tomorrow = Deadline.objects.filter(
            user=request.user, done=False, date_deadline=(nowtime + datetime.timedelta(days=1)).date(),
        ).order_by("date_deadline")

        params = {
            'user': request.user,
            'mydeadlines': mydeadlines,
            'len_mydeadlines': len(mydeadlines),
            'nowtime': nowtime,
            'deadlines_for_tomorrow': deadlines_for_tomorrow,
            'len_deadlines_for_tomorrow': len(deadlines_for_tomorrow),
        }

        return render(request, 'authed.html', params)

    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


def logoutp(request):
    if request.method == 'GET':
        logout(request)
        return redirect('/')
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def adddeadline(request):
    if not request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.title = deadline.description.split('\n')[0][:255]
            deadline.description = "\n".join(deadline.description.split('\n')[1:])
            deadline.user = request.user
            deadline.save()
            return redirect('/')
    elif request.method == 'GET':
        form = DeadlineForm()
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
    return render(request, 'adddeadline.html', {'form': form})


def done_task(request):
    if not request.user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        deadline_id = request.GET.get('deadline', None)

        deadline = Deadline.objects.get(id=deadline_id)

        if deadline.user != request.user:
            return HttpResponse('Access denied, this deadline is not associated with authed user')

        deadline.done = True
        deadline.save()

        return redirect('/')
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


def all_tasks(request):
    if not request.user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        tasks = Deadline.objects.filter(user=request.user).order_by("-date_deadline")
        nowtime = timezone.now()

        for i in range(len(tasks)):
            tasks[i].is_timeout = (tasks[i].date_deadline - nowtime).total_seconds() <= 0

        params = {
            'user': request.user,
            'tasks': tasks,
            'len_tasks': len(tasks),
        }

        return render(request, 'all_tasks.html', params)

    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
