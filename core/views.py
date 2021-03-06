from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm, DeadlineForm, TipForm, UserForm
from core.models import Deadline, Tip
from django.utils import timezone
import datetime
from secrets import token_hex
from django.conf import settings
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@require_http_methods(["GET"])
def main_page(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        return render(request, 'main.html', )


@require_http_methods(["GET", "POST"])
def loginp(request):
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
    return render(request, 'login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def registerp(request):
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
    return render(request, 'register.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def authed(request):
    mydeadlines = Deadline.objects.filter(user=request.user).order_by("-date_deadline")
    nowtime = timezone.now()

    for i in range(len(mydeadlines)):
        mydeadlines[i].is_timeout = (mydeadlines[i].date_deadline - nowtime).total_seconds() <= 0


    deadlines_for_tomorrow = Deadline.objects.filter(
        user=request.user, done=False, date_deadline=(nowtime + datetime.timedelta(days=1)).date(),
    ).order_by("date_deadline")

    tips = Tip.objects.filter(user=request.user, is_active=True)

    params = {
        'user': request.user,
        'mydeadlines': mydeadlines,
        'len_mydeadlines': len(mydeadlines),
        'nowtime': nowtime,
        'deadlines_for_tomorrow': deadlines_for_tomorrow,
        'len_deadlines_for_tomorrow': len(deadlines_for_tomorrow),
        'tips': tips,
    }

    return render(request, 'authed.html', params)


@login_required
@require_http_methods(["GET"])
def logoutp(request):
    logout(request)
    return redirect('/')


@login_required
@require_http_methods(["GET", "POST"])
def adddeadline(request):
    if request.method == 'POST':
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.user = request.user
            deadline.user_agent = request.META['HTTP_USER_AGENT']
            deadline.save()
            return redirect('/')
    elif request.method == 'GET':
        form = DeadlineForm()
    return render(request, 'adddeadline.html', {'form': form})


@login_required
@require_http_methods(["GET"])
def done_task(request):
    deadline_id = request.GET.get('deadline', None)

    deadline = Deadline.objects.get(id=deadline_id)

    if deadline.user != request.user:
        return HttpResponse('Access denied, this deadline is not associated with authed user')

    deadline.done = True
    deadline.save()

    return redirect('/')


@login_required
@require_http_methods(["GET"])
def all_tasks(request):
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


@login_required
@require_http_methods(["POST"])
def unpin_tip(request):
    tip_id = request.POST.get('id', None)

    tip = Tip.objects.get(id=tip_id)

    print(tip.user, request.user)

    if tip.user != request.user:
        return HttpResponse('Hey hacker, it is not your tip!')

    tip.is_active = False
    tip.save()

    return redirect('/')


@login_required
@require_http_methods(["GET", "POST"])
def add_tip(request):
    if request.method == 'POST':
        form = TipForm(request.POST)
        if form.is_valid():
            tip = form.save(commit=False)
            tip.user = request.user
            tip.save()
            return redirect('/')
    elif request.method == 'GET':
        form = TipForm()
    return render(request, 'addtip.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def profilep(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    elif request.method == 'GET':
        form = UserForm(instance=request.user)

    params = {'form': form, 'bot_name': settings.BOT_NAME}


    if request.user.profile.is_telegram_connected:
        params['telegram'] = True
        params['telegram_username'] = request.user.profile.telegram_username
        params['user'] = request.user
    else:
        params['telegram'] = False
        request.user.profile.telegram_hash = token_hex(20)
        request.user.profile.save()
        params['telegram_hash'] = request.user.profile.telegram_hash

    return render(request, 'profile.html', params)


@login_required
@require_http_methods(["GET"])
def unpin_telegram(request):
    user_id = request.GET.get('id', None)
    user = User.objects.get(id=user_id)

    p = user.profile
    p.is_telegram_connected = False
    p.save()

    return redirect('/profile')


@require_http_methods(["GET"])
def privacy_policy(request):
    return render(request, 'privacy.html')
