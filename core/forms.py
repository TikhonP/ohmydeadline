from django import forms
from django.contrib.auth.models import User
from core.models import Deadline, Tip
from django.contrib.auth.forms import UserCreationForm
import account.forms


class SignupForm(account.forms.SignupForm):

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]



class DeadlineForm(forms.ModelForm):
    class Meta:
        model = Deadline
        fields = ('date_deadline', 'working_time', 'description')


class TipForm(forms.ModelForm):
    class Meta:
        model = Tip
        fields = ('text', )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
