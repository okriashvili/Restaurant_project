from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView


# from user.forms import CustomUserCreationForm
from django.urls import reverse_lazy


# Create your views here.
# რეგისტრაციისათვის
class UserRegistrationView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('restaurant:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


# დასალოგინებლად
class UserLoginView(LoginView):
    template_name = 'login.html'
    next_page = reverse_lazy('restaurant:home')



# გამოსასვლელად
class UserLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('restaurant:home')



class UserProfileView(DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user













