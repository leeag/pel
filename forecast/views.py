# from distutils.msvc9compiler import MacroExpander
import json
import traceback
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage
from django.template import loader, Context

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
from django.forms.models import inlineformset_factory


from forms import UserRegistrationForm, SignupCompleteForm, CustomUserProfile, ForecastProposeForm, CommunityAnalysisForm, \
    ForecastVoteForm, CreateGroupForm, CustomInlineFormSet, AboutUserForm
from models import Forecast, ForecastPropose, ForecastVotes, ForecastVoteChoiceFinite, ForecastAnalysis, Group, Membership
from Peleus.settings import APP_NAME, FORECAST_FILTER, \
    FORECAST_FILTER_MOST_ACTIVE, FORECAST_FILTER_NEWEST, FORECAST_FILTER_CLOSING, FORECAST_FILTER_ARCHIVED, AREAS, REGIONS,GROUP_TYPES
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
        group = context['group']
        has_admin_rights = False

        if self.request.user.is_authenticated():
            try:
                has_admin_rights = Membership.objects.get(user=self.request.user, group=group).admin_rights
            except:
                has_admin_rights = False

        forecasts = Forecast.objects.distinct().filter(votes__user__membership__group=group, end_date__gte=date.today())
        followers = User.objects.filter(membership__group=group).exclude(membership__admin_group_approved=False)
        analysis = ForecastAnalysis.objects.filter(user__membership__group=group)

        if has_admin_rights:
            context['requests'] = User.objects.filter(membership__group=group, membership__admin_group_approved=False)
            context['has_admin_rights'] = has_admin_rights

        context['forecasts'], context['forecasts_count'], context['followers'], context['analysis'] = \
            forecasts, forecasts.count(), followers, analysis
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
        if self.request.user.is_authenticated():
            return Group.objects.exclude(membership__user=self.request.user).order_by('name')
        else:
            return Group.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(Users_and_Groups, self).get_context_data(**kwargs)
        context['user'] = self.request.user

        if 'areas' in self.request.GET:
            get_params = self.request.GET.get('areas')
            get_list_params = self.request.GET.getlist('areas')
            context['qstr'] = get_params
            users_by_areas = CustomUserProfile.objects.filter(forecast_areas__contains=get_params)
            if self.request.user.is_authenticated():
                context['profiles'] = User.objects.filter(custom=users_by_areas.exclude(user=self.request.user))
            else:
                context['profiles'] = User.objects.filter(custom=users_by_areas)

        elif 'region' in self.request.GET:
            get_params_region = self.request.GET.get('region')
            context['qstr_region'] = get_params_region
            users_by_regions = CustomUserProfile.objects.filter(forecast_regions__contains=get_params_region)
            if self.request.user.is_authenticated():
                context['profiles'] = User.objects.filter(custom=users_by_regions.exclude(user=self.request.user))
            else:
                context['profiles'] = User.objects.filter(custom=users_by_regions)
        else:
            if self.request.user.is_authenticated():
                context['profiles'] = User.objects.exclude(id=self.request.user.id).exclude(is_superuser=True).order_by('last_name')
            else:
                context['profiles'] = User.objects.all().exclude(is_superuser=True).order_by('last_name')
        return context


class JoinToGroup(View):

    def get(self, request):
        group_id = request.GET.get('group')
        group = get_object_or_404(Group, pk=group_id)
        curren_user = request.user
        group_type = group.type
        if curren_user.is_authenticated():
            if int(group_type) == 1:
                Membership(user=curren_user, group=group, admin_rights=False).save()
                return HttpResponse('followed')
            else:
                Membership(user=curren_user, group=group, admin_rights=False, admin_group_approved=False).save()
                return HttpResponse('request')
        else:
            return HttpResponse(status=404)


class AccessJoinGroup(View):

    def get(self, request):
        user_join = request.GET.get('user_join')
        group_join_id = request.GET.get('group_join')

        group = Group.objects.get(pk=group_join_id)
        user = User.objects.get(pk=user_join)

        membership = Membership.objects.get(user=user, group=group)
        membership.admin_group_approved = True
        membership.save()

        return HttpResponse('joined')

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
        form = ForecastProposeForm(data)
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
    Form = AboutUserForm
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
        groups_count = Group.objects.filter(membership__user=profile).count()
        analysis = profile.forecastanalysis_set.all()[:5]

        context['groups_count'], context['forecasts'], context['forecasts_archived'], context['analysis'] = \
            groups_count, forecasts, forecasts_archived, analysis

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


class ProfilePageGroupsView(ProfileViewMixin, DetailView):
    template_name = "profile_page_groups.html"
    model = User
    pk_url_kwarg = 'id'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
            context = super(ProfilePageGroupsView, self).get_context_data(**kwargs)
            profile = context.get('profile')
            analysis = profile.forecastanalysis_set.all()[:5]
            groups = Group.objects.filter(membership__user=profile)
            context['groups'], context['analysis'] = groups, analysis
            return context


from forms import ChoiceformSet
class ProposeForecastView(View):
    template_name = 'propose_forecast_page.html'
    template_name_access = 'propose_access.html'

    form = ForecastProposeForm

    def get(self, request):
        formset = ChoiceformSet()
        return render(request, self.template_name, {'form': self.form(), 'formset': formset})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            propose = form.save(commit=False)
            propose.user = request.user
            propose.save()

            if request.method == 'POST':
               formset = ChoiceformSet(request.POST, request.FILES, instance=propose)
            if formset.is_valid():
                formset.save()
                propose.save()
                form.save_m2m()
                return render(request, self.template_name_access, {})
            else:
                return render(request, self.template_name, {'form': form})
            return render(request, self.template_name, {"formset": formset})


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

    def get(self, request, token):

        res_dict = dict()
        try:
            user = CustomUserProfile.objects.get(activation_token=token)
            form = self.form(user)
        except User.DoesNotExist as ex:
            res_dict['error'] = ex
            return render(request, self.template_name, res_dict)
    # if token == user.custom.activation_token and datetime.now() <= user.custom.expires_at:
        if token == user.activation_token:
            user.email_verified = True
            res_dict['success'] = _('Email has been verified!')
            user.save()
            return render(request, self.template_name, {'form': form, 'success': res_dict['success'], 'token': token})

    def post(self, request, token):
        user_profile = CustomUserProfile.objects.get(activation_token=token)
        form = self.form(user_profile, request.POST)

        if form.is_valid():
            user_profile.conditions_accepted = True
            form.save()
            return HttpResponseRedirect(reverse('home'))

        else:
            return HttpResponseRedirect(reverse('errors'))
