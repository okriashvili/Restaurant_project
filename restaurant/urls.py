from django.urls import path
from restaurant.views import (
    IndexView, MenuListView, DishDetailView,
    CartView



)

from django.views.generic import TemplateView

app_name = 'restaurant'


urlpatterns = [
    path('', IndexView.as_view(), name='home' ),
    path('menu/', MenuListView.as_view(), name='menu' ),
    path('branch/', TemplateView.as_view(template_name='branches.html'), name='branch' ),
    path('dish/<int:product_pk>/', DishDetailView.as_view(), name='dish' ),
    path('order/', CartView.as_view(), name='order' ),
]






