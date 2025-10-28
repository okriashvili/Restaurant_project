from django.urls import path
from user.views import (
    UserRegistrationView,
    UserLoginView, UserLogoutView, UserProfileView,
    OrderDetailView,
)


app_name = 'user'


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),

]