import json
import traceback
from datetime import date, timedelta
from django.db.models.expressions import F
from django.db.transaction import commit

from django.shortcuts import render, get_object_or_404, render_to_response, RequestContext
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage
from django.template import loader, Context
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, DetailView, ListView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.defaults import page_not_found
from django.forms.models import inlineformset_factory
from django.http import JsonResponse


from forms import UserRegistrationForm, SignupCompleteForm, CustomUserProfile, ForecastProposeForm, CommunityAnalysisForm, \
    ForecastVoteForm, CreateGroupForm, CustomInlineFormSet, AboutUserForm, EditProfileForm, EditUserForm
from models import Forecast, ForecastVotes, ForecastAnalysis, Group, Membership, CustomUserProfile, Visitors, Followers
from Peleus.settings import APP_NAME, FORECAST_FILTER, \
    FORECAST_FILTER_MOST_ACTIVE, FORECAST_FILTER_NEWEST, FORECAST_FILTER_CLOSING, FORECAST_FILTER_ARCHIVED, AREAS, REGIONS,GROUP_TYPES
from context_processors import FORECAST_AREAS


class ForecastFilterMixin(object):
    def _queryset_by_tag(self, querydict, qs=None):
        forecasts = qs or Forecast.objects.all()
        tags = querydict.getlist('tag_area', [])
        # tag = querydict.get('tag')
        for tag in tags:
            # forecasts = forecasts.filter(tags__slug=tag)
            forecasts = forecasts.filter(forecast_areas__contains=tag)
        return forecasts

    def _queryset_by_tag_regions(self, querydict):
        tags_regions = querydict.getlist('tag_region', [])
        for tag in tags_regions:
            forecasts = Forecast.objects.filter(forecast_regions__contains=tag)
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

class UsersFilterMixin(object):

    def _get_profiles_icontains(self, param_users=None):
        profiles_by_username = User.objects.filter(username__icontains=param_users)
        profiles_by_first_name = User.objects.filter(first_name__icontains=param_users)
        profiles_by_last_name = User.objects.filter(last_name__icontains=param_users)
        profiles = profiles_by_first_name or profiles_by_last_name or profiles_by_username
        return profiles

    def _get_profiles_in(self, param_users=None):
        param_users = param_users.split()
        profiles_by_username = User.objects.filter(username__in=param_users)
        profiles_by_first_name = User.objects.filter(first_name__in=param_users)
        profiles_by_last_name = User.objects.filter(last_name__in=param_users)
        profiles = profiles_by_first_name or profiles_by_last_name or profiles_by_username
        return profiles

    def _get_users_by_params(self, param_users=None):
        profiles = self._get_profiles_icontains(param_users) or self._get_profiles_in(param_users)
        profiles_list = list(profiles.exclude(id=self.request.user.id))
        param_users_split = param_users.split()

        return profiles_list


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
        public_group = False
        is_member = False
        if self.request.user.is_authenticated():
            is_member = Membership.objects.filter(user=self.request.user, group=group).exists()
            try:
                has_admin_rights = Membership.objects.get(user=self.request.user, group=group).admin_rights
                public_group = Membership.objects.get(user=self.request.user, group=group).admin_group_approved
            except:
                has_admin_rights = False
            finally:
                if group.is_public_group():
                    public_group = group.is_public_group()
        else:
            if group.is_public_group():
                public_group = group.is_public_group()

        forecasts = Forecast.objects.distinct().filter(votes__user__membership__group=group, end_date__gte=date.today())
        followers = User.objects.filter(membership__group=group,\
                membership__admin_group_approved=True).exclude(membership__group=group, membership__admin_rights=True)
        analysis = ForecastAnalysis.objects.filter(user__membership__group=group)
        admins_group = User.objects.filter(membership__group=group, membership__admin_rights=True)

        if has_admin_rights:
            context['requests'] = User.objects.filter(membership__group=group, membership__admin_group_approved=False)
            context['has_admin_rights'] = has_admin_rights

        context['forecasts'], context['forecasts_count'], context['followers'], context['analysis'], context['public_group'], context['is_member'], context['admins_group'] =\
            forecasts, forecasts.count(), followers, analysis, public_group, is_member, admins_group
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


class Users_and_Groups(UsersFilterMixin, ListView):
    template_name = 'users_and_groups.html'
    model = Group
    paginate_by = 20

    def get_queryset(self):
        if 'q_us_gr' in self.request.GET and self.request.GET.get('q_us_gr'):
            param_groups = self.request.GET.get('q_us_gr')
            is_auth = self.request.user.is_authenticated()
            get_groups = Group.objects.filter(name__contains=param_groups)
            get_groups = get_groups.exclude(membership__user=self.request.user) if is_auth else get_groups
            return get_groups
        else:
            if self.request.user.is_authenticated():
                return Group.objects\
                    .exclude(membership__user=self.request.user)\
                    .annotate(num_membership=Count('membership'))\
                    .order_by('-num_membership')
            else:
                return Group.objects.all()\
                    .annotate(num_membership=Count('membership'))\
                    .order_by('-num_membership')

    def get_context_data(self, **kwargs):
        context = super(Users_and_Groups, self).get_context_data(**kwargs)
        context['user'] = self.request.user

        if 'areas' in self.request.GET:
            # get_params = self.request.GET.get('areas')
            get_list_params = self.request.GET.getlist('areas')
            # get_list_params.update({'areas':get_params})
            context['qstr'] = get_list_params
            users_by_areas = CustomUserProfile.objects.filter(forecast_areas__in=get_list_params)
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
        elif 'q_us_gr' in self.request.GET and self.request.GET.get('q_us_gr'):
            param_users = self.request.GET.get('q_us_gr')
            context['profiles'] = self._get_users_by_params(param_users)
            context['res'] = param_users
        else:
            if self.request.user.is_authenticated():
                exclude_superuser = User.objects.exclude(id=self.request.user.id).exclude(is_superuser=True)
                context['profiles'] = exclude_superuser.order_by('-date_joined')[:20]
            else:
                exclude_superuser = User.objects.all().exclude(is_superuser=True)
                context['profiles'] = exclude_superuser.order_by('-date_joined')[:20]
        return context


class JoinToGroup(View):

    def get(self, request):
        group_id = request.GET.get('group')
        group = get_object_or_404(Group, pk=group_id)
        curren_user = request.user
        is_exists_group = Membership.objects.filter(user=curren_user, group=group).exists()

        if curren_user.is_authenticated() and not is_exists_group:
            if group.is_public_group():
                Membership(user=curren_user, group=group, admin_rights=False).save()
                return HttpResponse('followed')
            else:
                Membership(user=curren_user, group=group, admin_rights=False, admin_group_approved=False).save()
                return HttpResponse('request')
        else:
            return HttpResponse(status=404)


class LeaveGroup(View):

    def get(self, request):
        group_id = request.GET.get('group_id')
        current_user = self.request.user
        if request.GET.get('user_id'):
            current_user = User.objects.get(pk=request.GET.get('user_id'))
        Membership.objects.filter(user=current_user, group__id=group_id).delete()

        is_ok = Membership.objects.filter(user=current_user, group__id=group_id).exists()
        if not is_ok:
            return HttpResponse('Leaved')

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
        qstr_region = None
        qstr_area = None
        forecasts = self._queryset_by_forecast_filter(request.GET).annotate(
            forecasters=Count('votes__user', distinct=True))
        if 'tag_area' in request.GET:
            forecasts = self._queryset_by_tag(request.GET, forecasts)
            qstr_area = request.GET.get('tag_area')
        elif 'tag_region' in request.GET:
            forecasts = self._queryset_by_tag_regions(request.GET)
            qstr_region = request.GET.get('tag_region')
        return render(request, self.template_name, {'data': forecasts, 'qstr_region': qstr_region, 'qstr_area': qstr_area})



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
        # context['uname'] = 'My' if owner else str(name_user) + "'s"
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


class CommunityAnalysisView(View):
    template_name = 'community_analysis_see_full_set.html'

    def get(self, request, id):
        forecast = get_object_or_404(Forecast, pk=id)
        analysis_set = forecast.forecastanalysis_set.all()

        return render(request, self.template_name,
                      {'forecast': forecast,
                       'analysis_set': analysis_set})


import json
from django.http import HttpResponse
class ProfileView(ProfileViewMixin, DetailView):
    form = AboutUserForm
    template_name = 'profile_page.html'
    model = User
    pk_url_kwarg = 'id'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        profile = context.get('profile')
        forecasts = Forecast.objects.distinct().filter(votes__user=profile, end_date__gte=date.today())[:5]
        forecasts_archived = Forecast.objects.distinct().filter(votes__user=profile, end_date__lt=date.today())[:5]
        groups_count = Group.objects.filter(membership__user=profile).count()
        analysis = profile.forecastanalysis_set.all()[:5]

        if not profile.is_superuser:
            context['about'] = CustomUserProfile.objects.get(user_id=profile.id)

        today = date.today()
        find_monday = today - timedelta(days=-today.weekday(), weeks=1)
        find_sunday = find_monday + timedelta(days=6)
        # counts = Visitors.objects.filter(datetime__range=[startdate, enddate]). \
        #     order_by('visited').filter(visited_id=self.request.user.id).count()
        visitors = Visitors.objects.filter(datetime__range=[find_monday, find_sunday], visited_id=self.request.user.id).order_by('-datetime')
        if not profile.is_superuser:
            context['about'] = CustomUserProfile.objects.get(user_id=profile.id)

        context['groups_count'], context['forecasts'], context['forecasts_archived'], context['analysis'], \
        context['visitors'] = groups_count, forecasts, forecasts_archived, analysis, visitors

        if not profile.id == self.request.user.id and self.request.user.is_authenticated():
            visit = Visitors()
            visit.visited = User.objects.get(pk=profile.id)
            visit.visitor = User.objects.get(pk=self.request.user.id)
            visit.save()

        return context

    def post(self, request, **kwargs):

        profile_id = kwargs.get('id')
        profile = CustomUserProfile.objects.get(user_id=profile_id)

        about_user = request.POST.get("about_user")
        profile.about_user = about_user
        profile.save()

        data = {}
        data['success'] = True
        data['about_user'] = about_user
        return HttpResponse(json.dumps(data), content_type='application/json')


class ProfileUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'edit_profile.html'
    model = User
    form_class = EditUserForm
    second_form_class = EditProfileForm
    pk_url_kwarg = 'id'
    success_message = 'Profile updated'

    def get_success_url(self):
        return reverse('edit_profile', kwargs={'id': self.request.user.id})


class GlobalSearchView(View):
    template_name = 'global_search.html'

    def get(self, request):
        params = request.GET.get('q')
        value = {}
        own_groups = []
        if params:
            if self.request.user.is_authenticated():
                groups = Group.objects.filter(name__icontains=params).exclude(membership__user=self.request.user)
                own_groups = Group.objects.filter(name__icontains=params, membership__user=self.request.user)
            else:
                groups = Group.objects.filter(name__icontains=params)
            users = User.objects.filter(username__contains=params)
            forecasts = Forecast.objects.filter(forecast_question__icontains=params)
            value = {
                'groups': groups,
                'users': users,
                'forecasts': forecasts,
                'own_groups': own_groups
            }
        return render(request, self.template_name, value)


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


