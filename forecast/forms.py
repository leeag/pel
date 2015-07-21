import django.forms as forms
from captcha.fields import ReCaptchaField
from datetime import date, datetime, timedelta
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from django.forms.extras import SelectDateWidget
from django.forms.models import BaseInlineFormSet
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import ugettext, ugettext_lazy as _
from taggit.forms import TagWidget
from django.forms.models import inlineformset_factory


from Peleus.settings import APP_NAME, TOKEN_EXPIRATION_PERIOD, TOKEN_LENGTH, DOMAIN_NAME, GROUP_TYPES

from forecast.models import CustomUserProfile, ForecastPropose, ForecastAnalysis, Forecast, ForecastVoteChoiceFinite, Group
from forecast.settings import ORGANIZATION_TYPE, AREAS, REGIONS, FORECAST_TYPE, FORECAST_TYPE_FINITE, \
    FORECAST_TYPE_MAGNITUDE, FORECAST_TYPE_PROBABILITY, FORECAST_TYPE_TIME_HORIZON
from utils.different import generate_activation_key


# from https://djangosnippets.org/snippets/2860/
class CSICheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def value_from_datadict(self, data, files, name):
        # Return a string of comma separated integers since the database, and
        # field expect a string (not a list).
        return ','.join(data.getlist(name))

    def render(self, name, value, attrs=None, choices=()):
        # Convert comma separated integer string to a list, since the checkbox
        # rendering code expects a list (not a string)
        if value:
            value = [int(i) for i in value.split(',')]
        return super(CSICheckboxSelectMultiple, self).render(
            name, value, attrs=attrs, choices=choices
        )


# Form field
class CSIMultipleChoiceField(forms.MultipleChoiceField):
    widget = CSICheckboxSelectMultiple

    # Value is stored and retrieved as a string of comma separated
    # integers. We don't want to do processing to convert the value to
    # a list like the normal MultipleChoiceField does.
    def to_python(self, value):
        return value

    def validate(self, value):
        # If we have a value, then we know it is a string of comma separated
        # integers. To use the MultipleChoiceField validator, we first have
        # to convert the value to a list.
        if value:
            value = value.split(',')
        super(CSIMultipleChoiceField, self).validate(value)


class CommunityAnalysisForm(Form):
    post_link = forms.URLField(required=False, label="Link to post", widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'Link to post (optional)'}))
    title = forms.CharField(required=True, max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Title'}))
    body = forms.CharField(required=True, max_length=1000, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Your post', 'rows': '4'}))

    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop('id')
        self.user = kwargs.pop('user')
        super(CommunityAnalysisForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        data = self.cleaned_data

        analysis = ForecastAnalysis(forecast_id=self.id, user=self.user, **data)
        analysis.save()


class CustomInlineFormSet(BaseInlineFormSet):
     pass

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        default_attrs_req = {'class': "form-control input-sm", 'required': 'required'}
        default_attrs = {'class': "form-control input-sm"}
        exclude = ('admin_approved',)
        # fields = '__all__'

        widgets = {'name': forms.TextInput(attrs=default_attrs_req),
                   'description': forms.Textarea(attrs=default_attrs),
                   'type': forms.Select(attrs=default_attrs_req),
                   'organization_type': forms.Select(attrs=default_attrs),
                   'region': forms.Select(attrs=default_attrs)
                   }


from django.forms.models import modelformset_factory, inlineformset_factory

ChoiceformSet = inlineformset_factory(ForecastPropose, ForecastVoteChoiceFinite, can_delete=False, extra=2,
                                      fields=['choice'],
                                      widgets={'choice': forms.TextInput(attrs={'class': "form-control input-sm"})})

class ForecastProposeForm(ModelForm):
    forecast_type = forms.ChoiceField(required=True, choices=FORECAST_TYPE,
                                      widget=forms.Select(attrs={'class': 'form-control input-sm'}))
    forecast_question = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = ForecastPropose
        fields = ('forecast_type', 'forecast_question', 'tags')
        widgets = {'tags': TagWidget(attrs={'class': "form-control input-sm"})}


class ForecastVoteChoiceFiniteForm(ModelForm):
    class Meta:
        model = ForecastVoteChoiceFinite
        fields = ('choice',)
        widgets = {'choice': forms.TextInput(attrs={'class': "form-control input-sm"})}


class ForecastVoteForm(forms.Form):
    class InitException(Exception):
        def __init__(self, forecast, user, *args, **kwargs):
            msg = "forecast" if forecast is None else "user"
            msg += " must be passed as an argument"
            super(ForecastVoteForm.InitException, self).__init__(msg, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.forecast = kwargs.pop('forecast', None)
        self.user = kwargs.pop('user', None)
        if self.forecast is None or self.user is None:
            raise self.InitException(self.forecast, self.user)

        super(ForecastVoteForm, self).__init__(*args, **kwargs)

        if self.forecast.forecast_type == FORECAST_TYPE_FINITE:
            self.fields['vote'] = forms.ChoiceField(
                required=True, choices=[(str(choice.id), choice.choice) for choice in self.forecast.choices.all()],
                widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'}))
        else:
            self.fields['vote'] = forms.IntegerField(
                required=True, widget=forms.NumberInput(
                    attrs={'class': 'form-control', 'required': 'required', 'min': self.forecast.min,
                           'max': self.forecast.max}))

    def save(self):
        if self.forecast.forecast_type == FORECAST_TYPE_FINITE:
            choice = self.forecast.choices.get(pk=self.cleaned_data['vote'])
            last_vote = self.forecast.votes.filter(user=self.user)
            if last_vote.count() == 0:
                self.forecast.votes.create(user=self.user, choice=choice, date=date.today())
            else:
                last_vote.update(choice=choice, date=date.today())
            return
        else:
            todays_vote = self.forecast.votes.filter(date=date.today(), user=self.user)
            if todays_vote.count() == 0:
                self.forecast.votes.create(user=self.user, date=date.today(), **self.cleaned_data)
            else:
                todays_vote.update(**self.cleaned_data)


class SignupCompleteForm(forms.Form):
    forecast_areas = CSIMultipleChoiceField(required=False, widget=CSICheckboxSelectMultiple, choices=AREAS)
    forecast_regions = CSIMultipleChoiceField(required=True, widget=CSICheckboxSelectMultiple, choices=REGIONS)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SignupCompleteForm, self).__init__(*args, **kwargs)

    def save(self):
        data = self.cleaned_data
        # user_profile = CustomUserProfile.objects.get(pk=user_id)
        # self.user.forecast_areas = [int(i) for i in data['forecast_areas']]
        # self.user.forecast_regions = [int(i) for i in data['forecast_regions']]
        self.user.forecast_areas = data['forecast_areas']
        self.user.forecast_regions = data['forecast_regions']
        self.user.save()
        return True

class AboutUserForm(ModelForm):
    #about_user = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input"}), required=False)
    #name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}), label=_('Name'))

    class Meta:
        model = CustomUserProfile
        fields = ("about_user",)
        widgets = {'About user': forms.Textarea(attrs={'class': "form-control input"})}

    def save(self, *args, **kw):
        super(AboutUserForm, self).save(*args, **kw)
        #self.instance.user.about_user = self.cleaned_data.get('about_user')
        self.instance.user.save()

    # def save(self, commit=True):
    #         user = super(AboutUserForm, self).save(commit=False)
    #         user.about_user = self.cleaned_data['about_user']
    #
    #         if commit:
    #             user.save()
    #
    #         return user


class UserRegistrationForm(ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}), label=_('Name'))
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}), label=_('Surname'))
    display_only_username = forms.BooleanField(widget=forms.CheckboxInput(),
                                               label=_("Please only display my Username on {}").format(APP_NAME),
                                               required=False)
    agree_with_terms = forms.BooleanField(widget=forms.CheckboxInput(),
                                          label=_("I agree to {}'s Terms of Use").format(APP_NAME), required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm",
                                                             'humanReadable': 'username'}), label=_('Username'))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control input-sm"}),
                               label=_("Password"))
    password_conf = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control input-sm"}),
                                    label=_('Confirm Password'))
    captcha = ReCaptchaField()
    organization = forms.ChoiceField(widget=forms.RadioSelect(),
                                     choices=ORGANIZATION_TYPE,
                                     label=_('Organization'), required=False)
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}),
                                        label=_('Name of organisation'), required=False)

    class Meta:
        model = CustomUserProfile
        fields = ("name", "surname", 'display_only_username', "username", "password",
                  "password_conf", "email", "country", "city", "profession", "position", 'organization_name',
                  "organization", "captcha", "agree_with_terms")
        exclude = ['user', 'activation_token', 'expires_at', 'email_verified']
        widgets = {'country': CountrySelectWidget(attrs={'class': "form-control input-sm"}),
                   'name': forms.TextInput(attrs={'class': "form-control input-sm"}),
                   'password': forms.TextInput(attrs={'class': "form-control input-sm"}),
                   'city': forms.TextInput(attrs={'class': "form-control input-sm"}),
                   'profession': forms.TextInput(attrs={'class': "form-control input-sm"}),
                   'position': forms.TextInput(attrs={'class': "form-control input-sm"}),
                   }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password_conf")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        data = self.cleaned_data
        user = User.objects.create_user(username=data['username'], first_name=data['name'], last_name=data['surname'],
                                        email=data['email'],
                                        password=data['password'])
        user.save()
        token = generate_activation_key(TOKEN_LENGTH)
        expire_date = datetime.now() + timedelta(hours=TOKEN_EXPIRATION_PERIOD)
        user_profile = CustomUserProfile(user=user, country=data['country'], city=data['city'],
                                         profession=data['profession'], position=data['position'],
                                         organization_name=data['organization_name'],
                                         organization=data['organization'],
                                         display_only_username=data['display_only_username'],
                                         activation_token=token,
                                         expires_at=expire_date)
        user_profile.save()
        try:
            EmailMessage('Confirm your email', '%s/confirm_email/%s' % (DOMAIN_NAME, token), to=[user.email]).send()
        except Exception as ex:
            print ex
        return user
