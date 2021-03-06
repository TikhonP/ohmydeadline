# Generated by Django 3.1.1 on 2020-10-20 11:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20201009_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deadline',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='deadline',
            name='date_deadline',
            field=models.DateTimeField(verbose_name='Дата дедлайна'),
        ),
        migrations.AlterField(
            model_name='deadline',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='deadline',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='deadline',
            name='working_time',
            field=models.IntegerField(verbose_name='Время выполнения'),
        ),
        migrations.AlterField(
            model_name='tip',
            name='text',
            field=models.CharField(max_length=500, verbose_name='Содержание заметки'),
        ),
    ]
