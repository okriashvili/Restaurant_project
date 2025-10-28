from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView
from django.shortcuts import render

from restaurant.models import Order, OrderItem

# from user.forms import CustomUserCreationForm
from django.urls import reverse_lazy

from user.models import Profile


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



class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_orders = Order.objects.filter(user=self.request.user).order_by('-created_at')
        context['orders'] = user_orders
        
        total_spending = sum(order.total_price for order in user_orders)
        context['total_spending'] = total_spending
        
        return context



















class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        # Only allow users to see their own orders
        return Order.objects.filter(user=self.request.user)

















