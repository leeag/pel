import json
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, DetailView, ListView
from django.views.defaults import page_not_found

from forms import UserRegistrationForm, SignupCompleteForm, CustomUserProfile, ForecastForm, CommunityAnalysisForm, \
    ForecastVoteForm, CreateGroupForm, CustomInlineFormSet
from models import Forecast, ForecastPropose, ForecastVotes, ForecastAnalysis, Group, ForecastProposeFiniteChoice, Membership
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

    def get(self, request, token):
        # token = request.GET.get('token')
        res_dict = dict()
        try:
            user = CustomUserProfile.objects.get(activation_token=token)
        except User.DoesNotExist as ex:
            res_dict['error'] = ex
            return render(request, self.template_name, res_dict)
        # if token == user.custom.activation_token and datetime.now() <= user.custom.expires_at:
        if token == user.activation_token:
            user.email_verified = True
            res_dict['success'] = _('Email has been verified!')
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
        forecasts = Forecast.objects.distinct().filter(votes__user=self.request.user, end_date__gte=date.today())
        context['forecasts'], context['forecasts_count'], context['user_name'] = \
            forecasts, forecasts.count(), self.request.user.username.capitalize()
        return context

class MyGroupsView(ListView):
    template_name = "groups_view.html"
    model = Group

    def get_queryset(self):
        queryset = Group.objects.filter(membership__user=self.request.user)
        return queryset


class ProposeNewGroup(View):
    template_name = "propose_group.html"
    template_group_access = "propose_group_access.html"

    form = CreateGroupForm

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {'form': self.form(), 'user': user})

    def post(self, request):
        form = self.form(request.POST)
        current_user = request.user
        if form.is_valid():
            propose = Group(**form.cleaned_data)
            if request.user.is_superuser:
                propose.admin_approved = True
            else:
                propose.admin_approved = False
            propose.save()
            Membership(user=request.user, group=propose, admin_rights=True).save()
            return render(request, self.template_group_access, {'is_admin': current_user.is_superuser})


class Users_and_Groups(ListView):
    template_name = 'users_and_groups.html'
    model = Group

    def get_queryset(self):
        return Group.objects.exclude(membership__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(Users_and_Groups, self).get_context_data(**kwargs)
        context['users'] = CustomUserProfile.objects.exclude(id=self.request.user.id)
        return context


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
        # forecast = Forecast.objects.get(pk=id)
        forecast = get_object_or_404(Forecast, pk=id)
        analysis_set = forecast.forecastanalysis_set.all()#.annotate(avg_votes=Avg('analysis_votes__vote'))
        media_set = forecast.forecastmedia_set.all()
        vote_form = ForecastVoteForm(forecast=forecast, user=request.user)
        analysis_form = CommunityAnalysisForm(id=id, user=request.user)

        try:
            last_vote = forecast.votes.filter(user=user).order_by('-date')[0].get_vote()
        except:
            last_vote = None
        return render(request, self.template_name,
                      {'forecast': forecast,
                       'vote_form': vote_form,
                       'analysis_form': analysis_form,
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

        # if not user.is_superuser:
        #     if user is not None and user.custom.email_verified:  # and user.is_active:
        #         login(request, user)
        #         try:
        #             if not user.custom.conditions_accepted:
        #                 return HttpResponseRedirect(reverse('home'))
        #         except Exception:
        #             pass
        #         return HttpResponseRedirect(reverse('home'))
        #
        #     elif user is not None and not user.custom.email_verified:
        #         return render(request, "sing_in_invalid.html", {'not_email_confirmed': True})
        #
        #     else:
        #         # return HttpResponse(_('Invalid login or password'), status=400)
        #         return render(request, "sing_in_invalid.html", {'invalid_login': True})
        # else:
        #     login(request, user)
        #     return HttpResponseRedirect(reverse('home'))

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return HttpResponseRedirect(reverse('profile', kwargs={'id': user.id}))
            elif user.custom.email_verified:
                login(request, user)
                return HttpResponseRedirect(reverse('profile', kwargs={'id': user.id}))
            else:
                return render(request, "sing_in_invalid.html", {'email_not_confirmed': not user.custom.email_verified})
        else:
            return render(request, "sing_in_invalid.html", {'invalid_login': True})


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


class ProfileViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ProfileViewMixin, self).get_context_data(**kwargs)
        if 'profile' not in context:
            pk = self.kwargs.get('id')
            profile = get_object_or_404(User, pk=pk)
            context['profile'] = profile
        else:
            profile = context['profile']
        owner = self.request.user.id == profile.id
        context['owner'] = owner
        context['uname'] = 'My' if owner else profile.full_name() + "'s"
        context['predictions_count'] = ForecastVotes.objects.filter(user=profile).count()

        return context


class ProfileForecastAnalysisView(ProfileViewMixin, ListView):
    template_name = 'profile_forecast_analysis_page.html'
    context_object_name = 'analysis'

    def get_queryset(self):
        profile = get_object_or_404(User, pk=self.kwargs.get('id'))
        self.profile = profile
        return ForecastAnalysis.objects.filter(user=profile)

    def get_context_data(self, **kwargs):
        context = super(ProfileForecastAnalysisView, self).get_context_data(**kwargs)
        context['profile'] = self.profile
        context['hide_analysis_box'] = True
        return context


class ProfileView(ProfileViewMixin, DetailView):
    template_name = 'profile_page.html'
    model = User
    pk_url_kwarg = 'id'
    context_object_name = 'profile'

    # def get(self, request, id):
    #     owner = request.user.id == int(id)
    #     profile = get_object_or_404(User, pk=id)
    #     forecasts = Forecast.objects.distinct().filter(votes__user=profile, end_date__gte=date.today())[:5]
    #     forecasts_archived = Forecast.objects.distinct().filter(votes__user=profile, end_date__lt=date.today())[:5]
    #     analysis = profile.forecastanalysis_set.all()[:3]
    #     return render(request, self.template_name, {'owner': owner, 'profile': profile,
    #                                                 'forecasts': forecasts,
    #                                                 'forecasts_archived': forecasts_archived,
    #                                                 'analysis': analysis, })

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        profile = context.get('profile')
        forecasts = Forecast.objects.distinct().filter(votes__user=profile, end_date__gte=date.today())[:5]
        forecasts_archived = Forecast.objects.distinct().filter(votes__user=profile, end_date__lt=date.today())[:5]
        groups = Group.objects.filter(membership__user=profile).count()
        analysis = profile.forecastanalysis_set.all()[:5]

        context['groups'], context['forecasts'], context['forecasts_archived'], context['analysis'] = groups, forecasts, forecasts_archived, analysis

        return context


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
        inst = ForecastPropose()
        if form.is_valid():
            propose = form.save(commit=False)
            propose.user = request.user
            # if request.method == "POST":
            #     formset = CustomInlineFormSet(request.POST, request.FILES, instance=inst)
            #     if formset.is_valid():
            #         formset.save()

            propose.save()
            form.save_m2m()
            username = request.user.username
            return render(request, self.template_name_access, {'username': username})
        else:
            return render(request, self.template_name, {'form': form})


class ProfilePageGroupsView(ProfileViewMixin, ListView):
    template_name = "profile_page_groups.html"
    model = Group

    def get_queryset(self):
        queryset = Group.objects.filter(membership__user=self.request.user)
        return queryset


class SignUpView(View):
    template_name = 'sign_up_page.html'
    template_name_confirm = 'sing_up_confirm.html'
    error_template = 'error_login_page.html'
    form = UserRegistrationForm

    def get(self, request):
        form = self.form()
        return render(request, self.template_name, {'form': form, 'app_name': APP_NAME})

    def post(self, request):
        signup_form = UserRegistrationForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            request.session['uid'] = user.id
            return render(request, self.template_name_confirm, {})
        else:
            # return render(request, self.error_template, {'errors': signup_form.errors})
            return render(request, self.template_name, {'form': self.form})


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
