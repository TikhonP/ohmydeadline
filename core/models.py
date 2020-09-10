from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Deadline(models.Model):
    title = models.CharField(max_length=255)
    date_created = models.DateTimeField(('date_created'), default=timezone.now)
    date_deadline = models.DateTimeField(('Date'))
    working_time = models.IntegerField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
