from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    is_telegram_connected = models.BooleanField(default=False)
    telegram_hash = models.CharField(max_length=40, unique=True, null=True, default=None)
    telegram_id = models.CharField(max_length=64, null=True, default=None)
    telegram_username = models.CharField(max_length=32, null=True, default=None)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Deadline(models.Model):
    title = models.CharField(verbose_name='Название', max_length=255)
    date_created = models.DateTimeField(verbose_name='Дата создания', default=timezone.now)
    date_deadline = models.DateTimeField(verbose_name='Дата дедлайна')
    working_time = models.IntegerField(verbose_name='Время выполнения')
    description = models.TextField(verbose_name='Описание')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    user_agent = models.CharField(max_length=200, default="None")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.title = self.description.split('\n')[0][:255]
            self.description = "\n".join(self.description.split('\n')[1:])

        super(Deadline, self).save(*args, **kwargs)


class Tip(models.Model):
    text = models.CharField(verbose_name='Содержание заметки', max_length=500)
    date_created = models.DateTimeField(('date_created'), default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
