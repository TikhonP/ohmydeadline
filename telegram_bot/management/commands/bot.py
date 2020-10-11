from django.core.management.base import BaseCommand
from django.conf import settings

from telegram import Bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.utils.request import Request
import telegram

from core.models import Deadline, Tip, Profile
from django.contrib.auth.models import User

import datetime
from django.utils import timezone
import threading
import time


def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


def start(update, context):
    unique_code = extract_unique_code(update.message.text)
    if unique_code:
        profile = Profile.objects.get(telegram_hash=unique_code)
        if profile is not None:
            profile.is_telegram_connected = True
            profile.telegram_id = update.message.from_user.id
            profile.telegram_username = update.message.from_user.username
            profile.save()
            reply = """Привет {}, как ты?

Вот команды, которые ты можешь использовать:
- Показать список задач на завтра /tomorrow_tasks
- Показать список всех активных задач /all_active_tasks
- Отвязать аккаунт /logout

Каждые 24 часа бот будет присылать тебе список задач на завтра.
                    """.format(profile.user.first_name)
        else:
            reply = "Какая-то ошибка, я не знаю кто ты..."
    else:
        if len(Profile.objects.filter(
            telegram_id=update.message.from_user.id,
            is_telegram_connected=True
        )) != 0:
            reply = "Ты уже подключен!"
        else:
            reply = "Пожалуйста, залогинься через ссылку на сайте."
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


def showlist_for_tomorrow(update, context):
    user = Profile.objects.get(telegram_id=update.message.from_user.id).user if len(Profile.objects.filter(telegram_id=update.message.from_user.id, is_telegram_connected=True))!=0 else None
    if user is None:
        reply = "Пожалуйста, залогинься через ссылку на сайте."
    else:
        nowtime = timezone.now()

        deadlines_for_tomorrow = Deadline.objects.filter(
                user=user,
                done=False,
                date_deadline=(nowtime + datetime.timedelta(days=1)).date(),
            ).order_by("date_deadline")
        if len(deadlines_for_tomorrow) > 0:
            reply = "*Твои задачи на завтра*:\n\n"
            for deadline in deadlines_for_tomorrow:
                d = "*-* __{}__{}\nДедлайн - {}\n\n".format(
                    deadline.title,
                    '\n'+deadline.description if deadline.description != '' else '',
                    deadline.date_deadline.strftime('%d.%m.%Y'),
                )
                reply += d
        else:
            reply = "У тебя нет задач на завтра!"

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                             parse_mode=telegram.ParseMode.MARKDOWN)


def showlist_of_all_active_tasks(update, context):
    user = Profile.objects.get(telegram_id=update.message.from_user.id).user if len(Profile.objects.filter(telegram_id=update.message.from_user.id, is_telegram_connected=True))!=0 else None
    if user is None:
        reply = "Пожалуйста, залогинься через ссылку на сайте."
    else:
        mydeadlines = Deadline.objects.filter(user=user).order_by("-date_deadline")

        if len(mydeadlines) > 0:
            nowtime = timezone.now()

            reply = "*Твои невыполненные задачи*:\n\n"
            for deadline in mydeadlines:
                if (deadline.date_deadline - nowtime).total_seconds() >= 0:
                    d = "*-* __{}__{}\nДедлайн - {}\n\n".format(
                        deadline.title,
                        '\n'+deadline.description if deadline.description != '' else '',
                        deadline.date_deadline.strftime('%d.%m.%Y'),
                    )
                    reply += d

        else:
            reply = "У тебя нет грядущих задач"

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply,
                             parse_mode=telegram.ParseMode.MARKDOWN)



def logout(update, context):
    user = Profile.objects.get(telegram_id=update.message.from_user.id).user if len(Profile.objects.filter(telegram_id=update.message.from_user.id, is_telegram_connected=True))!=0 else None
    if user is None:
        reply = "Пожалуйста, залогинься через ссылку на сайте."
    else:
        p = user.profile
        p.is_telegram_connected  = False
        p.save()
        reply = "Аккаунт отвязан."

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


def send_tasks(bot):
    while True:
        p = Profile.objects.filter(is_telegram_connected=True)

        nowtime = timezone.now()

        for u in p:
            deadlines_for_tomorrow = Deadline.objects.filter(
                    user=u.user,
                    done=False,
                    date_deadline=(nowtime + datetime.timedelta(days=1)).date(),
                ).order_by("date_deadline")
            if len(deadlines_for_tomorrow) > 0:
                reply = "Доброе утро!\n\n*Твои задачи на завтра*:\n\n"
                for deadline in deadlines_for_tomorrow:
                    d = "*-* __{}__{}\nДедлайн - {}\n\n".format(
                        deadline.title,
                        '\n'+deadline.description if deadline.description != '' else '',
                        deadline.date_deadline.strftime('%d.%m.%Y'),
                    )
                    reply += d
            else:
                reply = "У тебя нет задач на завтра!\n\nПланируй быстрее!"

            bot.send_message(chat_id=u.telegram_id, text=reply,
                             parse_mode=telegram.ParseMode.MARKDOWN)

        time.sleep(60)


class Command(BaseCommand):
    help = 'Telegram_Bot'

    def handle(self, *args, **options):
        request = Request(
            con_pool_size=8,
        )
        bot = Bot(
            request=request,
            token=settings.BOT_TOKEN
        )
        print("Connected to '{}' bot.".format(bot.get_me()['first_name']))

        updater = Updater(
            bot=bot,
            use_context=True
        )
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)

        showlist_for_tomorrow_handler = CommandHandler('tomorrow_tasks', showlist_for_tomorrow)
        dispatcher.add_handler(showlist_for_tomorrow_handler)

        showlist_of_all_active_tasks_handler = CommandHandler('all_active_tasks', showlist_of_all_active_tasks)
        dispatcher.add_handler(showlist_of_all_active_tasks_handler)

        logout_handler = CommandHandler('logout', logout)
        dispatcher.add_handler(logout_handler)

        t = threading.Thread(target=send_tasks, args=(bot, ))
        t.start()

        updater.start_polling()
