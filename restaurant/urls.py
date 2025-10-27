from django.urls import path

from restaurant.views import (
    IndexView, MenuListView, DishDetailView, SubmitRatingView,
    AddToCartView, OrderListView, ConfirmOrderView,
    RemoveFromCartView, UpdateCartView
)

from django.views.generic import TemplateView

app_name = 'restaurant'


urlpatterns = [
    path('', IndexView.as_view(), name='home' ),
    path('menu/', MenuListView.as_view(), name='menu' ),
    path('branch/', TemplateView.as_view(template_name='branches.html'), name='branch' ),
    path('dish/<int:product_pk>/', DishDetailView.as_view(), name='dish' ),
    path('dish/<int:dish_id>/rate/', SubmitRatingView.as_view(), name='rate_dish'),
    path('cart/', OrderListView.as_view(), name='cart' ),
    path('cart/confirm/', ConfirmOrderView.as_view(), name='confirm_order'),

    path('cart/add/<int:dish_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
]






