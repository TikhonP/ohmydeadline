# Generated by Django 3.1.1 on 2020-10-20 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201020_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadline',
            name='user_agent',
            field=models.CharField(default='None', max_length=200),
        ),
    ]
