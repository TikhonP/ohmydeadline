from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from core.forms import SignupForm, DeadlineForm, TipForm, UserForm
from core.models import Deadline, Tip
from django.utils import timezone
import datetime
from secrets import token_hex
from django.conf import settings
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from account.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import account.views
import account.forms


class SignupView(account.views.SignupView):
    form_class = SignupForm
    identifier_field = 'email'

    def generate_username(self, form):
        username = form.cleaned_data['email'].lower()
        return username


class LoginView(account.views.LoginView):

    form_class = account.forms.LoginEmailForm


@require_http_methods(["GET"])
def main_page(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        return render(request, 'main.html', )


@require_http_methods(["GET", "POST"])
def loginp(request):
    redirect_path = request.GET.get('redirect_uri', '/')
    if request.user.is_authenticated:
        return redirect(redirect_path)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user_cache)
            print(redirect_path)
            return redirect(redirect_path)
    else:
        form = AuthenticationForm(request)

    return render(request, 'auth/login.html', {
        'form': form,
        'redirect_path': redirect_path if redirect_path!='/' else False,
    })


@require_http_methods(["GET", "POST"])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

        messages.info(request, 'Спасибо за подтверждение аккаунта. Теперь вы можете пользоваться сервисом.')
        return authed(request)
    else:
        message.error(request, "Неверная ссылка")
        return render(request, 'auth/message.html')


@require_http_methods(["GET", "POST"])
def registerp(request):
    redirect_path = request.GET.get('redirect_uri', '/')
    if request.user.is_authenticated:
        return redirect(redirect_path)

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)

            mail_subject = 'Активируйте аккаунт "ohmydeadlines"'
            message = render_to_string('auth/confirm_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            # to_email = form.cleaned_data.get('email')
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            # email.send()

            message.info(request, "Пожалуйста подвердите аккаунт, перейдя по ссылке в письме на указанной почте.")
            print("=="*10+"\n"+message+"\n")
            return render(request, 'auth/message.html')

    elif request.method == 'GET':
        form = RegisterForm()
    return render(request, 'auth/register.html', {
        'form': form,
        'redirect_path': redirect_path if redirect_path!='/' else False,
    })


'''
@require_http_methods(["GET", "POST"])
def registerp(request):
    redirect_path = request.GET.get('redirect_uri', '/')
    if request.user.is_authenticated:
        return redirect(redirect_path)

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(redirect_path)
    elif request.method == 'GET':
        form = UserCreationForm()
    return render(request, 'register.html', {
        'form': form,
        'redirect_path': redirect_path if redirect_path!='/' else False,
    })
'''



@login_required(redirect_field_name='redirect_uri')
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

    return render(request, 'authed/authed.html', params)


@login_required(redirect_field_name='redirect_uri')
@require_http_methods(["GET"])
def logoutp(request):
    logout(request)
    return redirect('/')


@login_required(redirect_field_name='redirect_uri')
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
    return render(request, 'authed/adddeadline.html', {'form': form})


@login_required(redirect_field_name='redirect_uri')
@require_http_methods(["GET"])
def done_task(request):
    deadline_id = request.GET.get('deadline', None)

    deadline = Deadline.objects.get(id=deadline_id)

    if deadline.user != request.user:
        return HttpResponse('Access denied, this deadline is not associated with authed user')

    deadline.done = True
    deadline.save()

    return redirect('/')


@login_required(redirect_field_name='redirect_uri')
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

    return render(request, 'authed/all_tasks.html', params)


@login_required(redirect_field_name='redirect_uri')
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


@login_required(redirect_field_name='redirect_uri')
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
    return render(request, 'authed/addtip.html', {'form': form})


@login_required(redirect_field_name='redirect_uri')
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

    return render(request, 'auth/profile.html', params)


@login_required(redirect_field_name='redirect_uri')
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
    return render(request, 'static_templates/privacy.html')
