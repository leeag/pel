import json
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, DetailView, ListView

from forms import UserRegistrationForm, SignupCompleteForm, CustomUserProfile, ForecastForm, CommunityAnalysisForm, \
    ForecastVoteForm
from models import Forecast, ForecastPropose, ForecastVotes, ForecastAnalysis, Group
from Peleus.settings import APP_NAME, FORECAST_FILTER, \
    FORECAST_FILTER_MOST_ACTIVE, FORECAST_FILTER_NEWEST, FORECAST_FILTER_CLOSING, FORECAST_FILTER_ARCHIVED
# from postman.models import Message


class ForecastFilterMixin(object):
    def _queryset_by_tag(self, querydict, qs=None):
        forecasts = qs or Forecast.objects.all()
        tags = querydict.getlist('tag', [])
        for tag in tags:
            forecasts = forecasts.filter(tags__slug=tag)

        return forecasts

    def _queryset_by_forecast_filter(self, querydict, qs=None):
        """
        Allows to build queryset by filter in GET-request.
        E.g. ?filter=mostactive will select the most active forecasts
        """
        forecasts = qs or Forecast.active.all()
        forecast_filter = querydict.get(FORECAST_FILTER, FORECAST_FILTER_MOST_ACTIVE)

        if forecast_filter == FORECAST_FILTER_MOST_ACTIVE:
            forecasts = forecasts.annotate(num_votes=Count('votes')).order_by('-num_votes')
        elif forecast_filter == FORECAST_FILTER_NEWEST:
            forecasts = forecasts.annotate(num_votes=Count('votes')).order_by('-start_date')
        elif forecast_filter == FORECAST_FILTER_CLOSING:
            forecasts = forecasts.annotate(num_votes=Count('votes')).order_by('end_date')
        elif forecast_filter == FORECAST_FILTER_ARCHIVED:
            forecasts = Forecast.archived.all()
        return forecasts

    def _get_url_without_tag(self, path, querydict):
        params = QueryDict(querydict.urlencode(), mutable=True)
        params.pop('tag')

        return path + '?' + params.urlencode()


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class ActiveForecastsView(ForecastFilterMixin, View):
    template_name = 'forecasts_page.html'

    def get(self, request):
        forecasts = Forecast.active.all()
        if 'tag' in request.GET:
            forecasts = self._queryset_by_tag(request.GET, forecasts)
        forecasts = self._queryset_by_forecast_filter(request.GET, forecasts)
        return render(request, self.template_name, {'data': forecasts, 'is_active': True})


class ActiveForecastVoteView(View):
    Form = ForecastVoteForm
    def post(self, request):
        data = request.POST
        forecast_id = data.get('forecast-id', None)

        # vote = data.get('forecast-vote', None)
        if not forecast_id:
            return HttpResponseRedirect(reverse('individual_forecast', kwargs={'id': forecast_id}))
        forecast = Forecast.objects.get(pk=forecast_id)
        if forecast.is_active() and request.user.is_authenticated():
            form = self.Form(data, forecast=forecast, user=request.user)

            if form.is_valid():
                form.save()

            # todays_vote = forecast.votes.filter(date=date.today(), user=request.user)
            # if todays_vote.count() == 0:
            #     forecast.votes.create(user=request.user, vote=vote, date=date.today())
            # else:
            #     todays_vote.update(vote=vote)

        return HttpResponseRedirect(reverse('individual_forecast', kwargs={'id': forecast_id}))


class ArchivedForecastsView(ForecastFilterMixin, View):
    template_name = 'forecasts_page.html'

    def get(self, request):
        forecasts = Forecast.archived.all()
        if 'tag' in request.GET:
            forecasts = self._queryset_by_tag(request.GET, forecasts)
        return render(request, self.template_name, {'data': forecasts, 'is_active': False})


class CommunityAnalysisPostView(View):
    def post(self, request, id):
        form = CommunityAnalysisForm(request.POST, id=id, user=request.user)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('individual_forecast', kwargs={'id': id}))


class EmailConfirmationView(View):
    template_name = 'email_confirm_page.html'

    def get(self, request):
        token = request.GET.get('token')
        res_dict = dict()
        try:
            user = CustomUserProfile.objects.get(activation_token=token)
        except User.DoesNotExist as ex:
            res_dict['error'] = ex
            return render(request, self.template_name, res_dict)
        if token == user.customuserprofile.activation_token and datetime.now() <= user.customuserprofile.expires_at:
            user.email_verified = True
            res_dict['success'] = _('Email was verified!')
            user.save()
        else:
            res_dict['error'] = _('Provided token is incorrect or expired')
        return render(request, self.template_name, res_dict)


class ForecastsJsonView(ForecastFilterMixin, View):
    def get(self, request):
        qs = Forecast.objects.all()

        if 'id' in request.GET:
            qs = qs.filter(pk__in=request.GET.getlist('id'))
        elif 'tag' in request.GET:
            qs = self._queryset_by_tag(request.GET, qs)
        elif 'uid' in request.GET:
            type = request.GET.get('type', 'archived')
            qs = Forecast.active.distinct().all() if type == 'active' else Forecast.archived.distinct().all()
            qs = qs.filter(votes__user_id=request.GET.get('uid'))
        else:
            qs = self._queryset_by_forecast_filter(request.GET)
        return self._respond(qs)

    def _respond(self, forecasts):
        return HttpResponse(json.dumps([f.to_json() for f in forecasts]),
                            content_type='application/json')


class GroupView(DetailView):
    template_name = 'group_page.html'
    model = Group
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(GroupView, self).get_context_data(**kwargs)
        return context

class MyGroupsView(ListView):
    template_name = "groups_view.html"
    model = Group

    def get_queryset(self):
        queryset = Group.objects.filter(membership__user=self.request.user)
        return queryset



class IndexPageView(ForecastFilterMixin, View):
    template_name = 'index_page.html'

    def get(self, request):
        forecasts = self._queryset_by_forecast_filter(request.GET).annotate(
            forecasters=Count('votes__user', distinct=True))
        if 'tag' in request.GET:
            forecasts = self._queryset_by_tag(request.GET, forecasts)

        return render(request, self.template_name, {'data': forecasts})


class IndividualForecastView(View):
    template_name = 'individual_forecast_page.html'

    def get(self, request, id):
        user = request.user
        forecast = Forecast.objects.get(pk=id)
        analysis_set = forecast.forecastanalysis_set.all()
        media_set = forecast.forecastmedia_set.all()
        vote_form = ForecastVoteForm(forecast=forecast, user=request.user)

        try:
            last_vote = forecast.votes.filter(user=user).order_by('-date')[0].vote
        except:
            last_vote = None
        return render(request, self.template_name,
                      {'forecast': forecast,
                       'vote_form': vote_form,
                       'analysis_set': analysis_set,
                       'media_set': media_set,
                       'last_vote': last_vote,})


class LoginView(View):

    def post(self, request):
        request.session.set_test_cookie()
        if not request.session.test_cookie_worked():
            return HttpResponse(_("Please enable cookies and try again."))
        request.session.delete_test_cookie()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:  # and user.is_active:
            login(request, user)
            try:
                if not user.customuserprofile.conditions_accepted:
                    return HttpResponseRedirect(reverse('signup2'))
            except Exception:
                pass
            return HttpResponseRedirect(reverse('home'))
        else:
            # return HttpResponse(_('Invalid login or password'), status=400)
            return render(request, "sing_in_invalid.html", {})


class LogoutView(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        return HttpResponseRedirect(reverse('home'))


class PlaceVoteView(View):
    def post(self, request):
        data = request.POST
        user = request.user
        form = ForecastForm(data)
        if not form.is_valid():
            return HttpResponse(_('Invalid input data!'), status=400)
        forecast = get_object_or_404(Forecast, pk=data.get('fid'))
        f_vote = ForecastVotes.objects.filter(user__eq=user.id, forecast__eq=forecast.id)
        if f_vote:
            f_vote.update(vote=data.get('vote'))
            f_vote.save()
        else:
            new_f_vote = ForecastVotes(user=request.user, forecast=forecast, vote=data.get('vote'))
            new_f_vote.save()
        return HttpResponse('ok')


class ProfileView(View):
    template_name = 'profile_page.html'

    def get(self, request, id):
        # messages_inbox = Message.objects.filter()
        owner = request.user.id == int(id)
        profile = get_object_or_404(User, pk=id)
        forecasts = Forecast.objects.distinct().filter(votes__user=profile, end_date__gte=date.today())[:5]
        forecasts_archived = Forecast.objects.distinct().filter(votes__user=profile, end_date__lt=date.today())[:5]

        return render(request, self.template_name, {'owner': owner, 'profile': profile,
                                                    'forecasts': forecasts,
                                                    'forecasts_archived': forecasts_archived})


class ProfileForecastView(View):
    template_name = 'forecasts.html'

    def get(self, request, id):
        profile = get_object_or_404(User, pk=id)
        forecasts = Forecast.objects.filter(votes__user=profile).distinct()
        if 'filter' in request.GET and request.GET.get('filter') == 'archived':
            forecasts = forecasts.filter(end_date__lt=date.today())
        else:
            forecasts = forecasts.filter(end_date__gte=date.today())

        return render(request, self.template_name,
                      {'is_active': True, 'data': forecasts, 'disable_tags': True})



class ProposeForecastView(View):
    template_name = 'propose_forecast_page.html'
    template_name_access = 'propose_access.html'

    form = ForecastForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form()})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            propose = form.save(commit=False)
            propose.user = request.user
            propose.save()
            form.save_m2m()
            username = request.user.username
            return render(request, self.template_name_access, {'username': username})
        else:
            return render(request, self.template_name, {'form': form})


class SignUpView(View):
    template_name = 'sign_up_page.html'
    error_template = 'error_login_page.html'
    form = UserRegistrationForm

    def get(self, request):
        form = self.form()
        return render(request, self.template_name, {'form': form, 'app_name': APP_NAME })

    def post(self, request):
        signup_form = UserRegistrationForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            request.session['uid'] = user.id
            return HttpResponseRedirect(reverse('signup2'))
        else:
            return render(request, self.error_template, {'errors': signup_form.errors})


class SignUpSecondView(View):
    template_name = 'sign_up2_page.html'
    form = SignupCompleteForm

    def get(self, request):
        form = self.form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            user_id = request.session.get('uid') or request.user.id
            user_profile = CustomUserProfile.objects.get(user=user_id)
            user_profile.conditions_accepted = True
            user_profile.save()
            form.save(user_id)
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponseRedirect(reverse('errors'))
