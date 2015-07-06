from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

import forecast.views as views
from Peleus.settings import MEDIA_ROOT

admin.autodiscover()
urlpatterns = patterns(
    '',
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'about/$', TemplateView.as_view(template_name='about_page.html'), name='about'),
    url(r'^$', views.IndexPageView.as_view(), name='home'),
    url(r'^profile/(?P<id>\d+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^profile/(?P<id>\d+)/analysis/$', views.ProfileForecastAnalysisView.as_view(), name='profile_forecast_analysis'),
    url(r'^profile/(?P<id>\d+)/groups/$', views.ProfilePageGroupsView.as_view(), name='profile_page_groups'),
    url(r'^group/(?P<id>\d+)/$', views.GroupView.as_view(), name='group'),
    url(r'^my_groups/$', views.MyGroupsView.as_view(), name='my_groups'),
    url(r'^users_groups/$', views.Users_and_Groups.as_view(), name='users_groups'),
    url(r'^join_group/$', views.JoinToGroup.as_view(), name='join_to_group'),
    url(r'signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'signuplast/$', views.SignUpSecondView.as_view(), name='signup2'),
    url(r'^confirm_email/(?P<token>\w+)$', views.EmailConfirmationView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^errors/$', TemplateView.as_view(template_name='error_login_page.html'), name='errors'),
    url(r'^active_forecasts/$', views.ActiveForecastsView.as_view(), name='active_forecasts'),
    url(r'^archived_forecasts/$', views.ArchivedForecastsView.as_view(), name='archived_forecasts'),
    url(r'^propose_forecast/$', views.ProposeForecastView.as_view(), name='propose_forecast'),
    url(r'^propose_group/$', views.ProposeNewGroup.as_view(), name='propose_group'),
    # ajax forecasts for profile
    url(r'^profile_forecasts/(?P<id>\d+)/$', views.ProfileForecastView.as_view(), name='profile_forecasts_ajax'),
    url(r'^forecast/(?P<id>\d+)/$', views.IndividualForecastView.as_view(), name='individual_forecast'),
    url(r'^forecasts/$', views.ForecastsJsonView.as_view(), name='forecasts'),
    url(r'^forecast_vote/$', views.ActiveForecastVoteView.as_view(), name='forecast_vote'),
    url(r'^forecast_analysis/(?P<id>\d+)/$', views.CommunityAnalysisPostView.as_view(), name='forecast_analysis'),
    url(r'^messages/', include('postman.urls')),
    # url(r'^messages/inbox/', views.ProfilePageSidebarView.as_view()),

    # TODO remove
    url(r'^404/$', TemplateView.as_view(template_name='404.html'))
) + static.static(settings.MEDIA_URL, document_root=MEDIA_ROOT)
