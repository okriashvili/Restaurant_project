from django import forms
from restaurant.models import Order, OrderItem, Rating


class BookingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'total_price']


class RatingForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = Rating
        fields = ['rating']

