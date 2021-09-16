from rest_framework import serializers
from core.models import Profile, Tip, Deadline


class TipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tip
        fields = ('text', )


class DeadlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deadline
        fields = ('title', 'date_deadline', 'working_time', 'description',)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('is_telegram_connected', 'telegram_hash', 'telegram_id', 'telegram_username',)
