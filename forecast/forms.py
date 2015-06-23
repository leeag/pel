import django.forms as forms
from captcha.fields import ReCaptchaField
from datetime import date, datetime, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from django.forms.extras import SelectDateWidget
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import ugettext, ugettext_lazy as _
from taggit.forms import TagWidget
from django.forms import MultiWidget

from Peleus.settings import APP_NAME, TOKEN_EXPIRATION_PERIOD, TOKEN_LENGTH, DEFAULT_EMAIL, DOMAIN_NAME, GROUP_TYPES

from forecast.models import CustomUserProfile, ForecastVotes, ForecastPropose, ForecastAnalysis, Forecast, Group
from forecast.settings import ORGANIZATION_TYPE, AREAS, REGIONS, FORECAST_TYPE, FORECAST_TYPE_FINITE, \
    FORECAST_TYPE_MAGNITUDE, FORECAST_TYPE_PROBABILITY, FORECAST_TYPE_TIME_HORIZON
from utils.different import generate_activation_key


# class RangeWidget(MultiWidget):
#     def __init__(self, attrs=None, *args, **kwargs):
#
#         _widgets = (
#             forms.HiddenInput(attrs=attrs),
#             forms.HiddenInput(attrs=attrs),
#         )
#         super(RangeWidget, self).__init__(_widgets, *args, **kwargs)
#
#     def decompress(self, value):
#         if value:
#             return [value.min(), value.max()]
#         return [min, max]
#
#     def format_output(self, rendered_widgets):
#         return u''.join(rendered_widgets) + unicode(self.media)
#
#     class Media:
#         css = {
#             'all': ('/static/3p/jquery-ui.min.css',)
#         }
#         js = ('/static/3p/jquery-ui.mis.js',
#               '/static/1p/range_votes.js')


class CommunityAnalysisForm(Form):

    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop('id')
        self.user = kwargs.pop('user')
        super(CommunityAnalysisForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        data = self.cleaned_data

        analysis = ForecastAnalysis(forecast_id=self.id, user=self.user, **data)
        analysis.save()


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


class ForecastForm(ModelForm):
    forecast_type = forms.ChoiceField(required=True, choices=FORECAST_TYPE,
                                      widget=forms.Select(attrs={'class': 'form-control input-sm'}))
    forecast_question = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = ForecastPropose
        fields = ('forecast_type', 'forecast_question', 'tags')
        widgets = {'tags': TagWidget(attrs={'class': "form-control input-sm"})}


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
                required=True, choices=[(str(choice.num), choice.choice) for choice in self.forecast.choices.all()],
                widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'}))
        elif self.forecast.forecast_type == FORECAST_TYPE_MAGNITUDE:
            self.fields['vote'] = forms.IntegerField(
                required=True, label='from', widget=forms.NumberInput(attrs={'class': 'form-control input-sm', 'required': 'required', 'min': self.forecast.min}))
            self.fields['vote2'] = forms.IntegerField(
                required=True, label='to', widget=forms.NumberInput(attrs={'class': 'form-control input-sm', 'required': 'required', 'max': self.forecast.max}))
            # self.fields['vote'] = forms.MultiValueField(widget=RangeWidget(attrs={'required': 'required', 'min': self.forecast.min,
            #                                                                       'max': self.forecast.max}))
        else:
            self.fields['vote'] = forms.IntegerField(
                required=True, widget=forms.NumberInput(
                    attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '100'}))

    def save(self):
        if self.forecast.forecast_type == FORECAST_TYPE_FINITE:
            choice = self.forecast.choices.get(num=self.cleaned_data['vote'])
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
    forecast_areas = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=AREAS)
    forecast_regions = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=REGIONS)

    def save(self, user_id):
        data = self.cleaned_data
        user_profile = CustomUserProfile.objects.get(user=user_id)
        user_profile.forecast_areas = [int(i) for i in data['forecast_areas']]
        user_profile.forecast_regions = [int(i) for i in data['forecast_regions']]
        user_profile.save()
        return True


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
    username = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control input-sm"}), label=_('Username'))
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
            send_mail('Confirm your email', '%s/confirm_email?token=%s' % (DOMAIN_NAME, token), DEFAULT_EMAIL,
                      [user.email])
        except Exception as ex:
            print ex

        return user
