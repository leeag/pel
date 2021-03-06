from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View

from forms import UserRegistrationForm, SignupCompleteForm, CustomUserProfile
from Peleus.settings import APP_NAME


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)


class EmailConfirmationView(View):
    template_name = 'email_confirm_page.html'

    def get(self, request, token):
        res_dict = dict()
        try:
            user = CustomUserProfile.objects.get(activation_token=token)
        except User.DoesNotExist as ex:
            res_dict['error'] = ex
            return render(request, self.template_name, res_dict)
        if token == user.activation_token:
            user.email_verified = True
            res_dict['success'] = 'Email was verified!'
            user.save()
        else:
            res_dict['error'] = 'Provided token is incorrect'
        return render(request, self.template_name, res_dict)


class LoginView(View):
    def post(self, request):
        request.session.set_test_cookie()
        if not request.session.test_cookie_worked():
            return HttpResponse("Please enable cookies and try again.")
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
            return HttpResponse('Invalid login or password', status=400)


class LogoutView(View):
    def get(self, request):
        response = logout(request)
        logout(request)
        request.session.flush()
        return HttpResponseRedirect(reverse('home'))


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
            signup_form.save()
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
            user = request.user
            user.customuserprofile.conditions_accepted = True
            user.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponseRedirect(reverse('errors'))

