from django.forms import ModelForm, DateInput, PasswordInput
from rushtracker.models import Rush
from organization.models import Organization
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from crispy_forms.bootstrap import PrependedText
from authentication.models import UserProfile
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Hidden
from django import forms
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from organization.forms import CreateOrganizationForm
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.conf import settings
from django.forms.models import ModelForm
from braces.forms import UserKwargModelFormMixin


class UserSignInForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserSignInForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.render_hidden_fields = True
        self.helper.form_tag = False

        self.helper.layout = Layout(
            PrependedText('username', '<span class="glyphicon glyphicon-user"></span>'),
            PrependedText('password', '<span class="glyphicon glyphicon-lock"></span>'),
        )
        
    def clean_username(self):
        return self.cleaned_data.get('username').lower()

class ChapterAdminForm(ModelForm):
    fraternity = forms.CharField(max_length=100, required=True)
    chapter = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(ChapterAdminForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError("Password mismatch")
        return password2

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(
                "Can't create User and UserProfile without database save")
        data = {
            'national_organization': self.cleaned_data['fraternity'],
            'chapter_name': self.cleaned_data['chapter']
        }
        self.organization = CreateOrganizationForm(data)
        self.organization = self.organization.save()
        user = super(ChapterAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.organization = self.organization
        user.save()
        perm = Permission.objects.get(codename='change_brotheruser')
        user.user_permissions.add(perm)
        perm2 = Permission.objects.get(codename='add_brotheruser')
        user.user_permissions.add(perm2)
        user.user_permissions.add(
            Permission.objects.get(codename='chapter_admin'),)
        user_profile = UserProfile(user=user)
        user_profile.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('',)
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))


class SingleUserCreationForm(ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SingleUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = '/authentication/createSingleUser'
        self.helper.form_id = 'form1'

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError("Password mismatch")
        return password2

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(
                "Must Commit as user profile needs a user to save")
        user = super(SingleUserCreationForm, self).save(commit=False)
        user.organization = self.request.user.organization
        user.set_password(self.cleaned_data["password1"])
        user.save()
        perm = Permission.objects.get(codename='delete_comment')
        user.user_permissions.add(perm)
        user_profile = UserProfile(user=user)
        user_profile.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')


class ChangePasswordForm(UserKwargModelFormMixin, ModelForm):
    old_password = forms.CharField(
        label="Old Password", widget=forms.PasswordInput)
    new_password = forms.CharField(
        label="New Password", widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(
            Submit('Submit', 'Submit', css_class='btn-primary'))

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("MUST COMMIT!")
        data = self.cleaned_data
        if self.user.check_password(data['old_password']) and data['new_password'] == data['new_password_confirm']:
            self.user.set_password(self.cleaned_data['new_password'])
            self.user.save()
            update_session_auth_hash(self.request, self.user)
            return self.user

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password', 'new_password_confirm']

class UserUpdateNameForm(ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        super(UserUpdateNameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('authentication:update_name', args=[self.request.user.pk])


