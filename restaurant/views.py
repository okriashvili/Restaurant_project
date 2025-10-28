
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, TemplateView,
    View, RedirectView, CreateView
)

from django.shortcuts import get_object_or_404

from restaurant.forms import BookingForm, RatingForm
from restaurant.models import Restaurant, Menu, Category, Order, OrderItem, Cart, CartItem, Rating


# მთავარი გვერდი
class IndexView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from django.db.models import Avg
        dishes_with_ratings = Menu.objects.select_related('category').prefetch_related(
            'ratings__user', 'branch'
        ).annotate(
            avg_rating=Avg('ratings__rating')
        ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:6]
        context['highest_rated'] = dishes_with_ratings

        # Most viewed dishes
        most_viewed = Menu.objects.select_related('category').prefetch_related(
            'ratings', 'branch'
        ).order_by('-views')[:6]
        context['most_viewed'] = most_viewed

        context['restaurant_branch'] = Restaurant.objects.all()
        
        return context




# კერძების ჩამონათვალი
class MenuListView(ListView):
    model = Menu
    template_name = 'menu.html'
    context_object_name = 'all_dish'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related(
            'branch', 'ratings__user'
        )
        # სერჩ ბარი
        search_query = self.request.GET.get('search')
        # სიცხარე
        spiciness_filter = self.request.GET.get('spiciness')
        # ვეჯი
        vegetarian_filter = self.request.GET.get('vegetarian')
        # ლაქტოზა
        gluten_free_filter = self.request.GET.get('gluten_free')

        # კატეგორიის მიხედვით (support both ?category= and ?categories=)
        categories_filter = self.request.GET.get('category') or self.request.GET.get('categories')


        if search_query:
            queryset = queryset.filter(Q(name__istartswith=search_query)|Q(name__icontains=search_query) )

        if categories_filter:
            try:
                # Try by ID first
                queryset = queryset.filter(category_id=int(categories_filter))
            except (TypeError, ValueError):
                # Fallback by name (case-insensitive)
                queryset = queryset.filter(category__category_name__iexact=categories_filter)

        if spiciness_filter:
            try:
                value = int(spiciness_filter)
                queryset = queryset.filter(spiciness__gte=value)
            except ValueError:
                pass

        if vegetarian_filter:
            is_vegetarian = vegetarian_filter.lower() == 'yes'
            queryset = queryset.filter(is_vegetarian=is_vegetarian)

        if gluten_free_filter:
            is_gluten_free = gluten_free_filter.lower() == 'yes'
            queryset = queryset.filter(is_gluten_free=is_gluten_free)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dishes_with_ratings = []
        for dish in context['all_dish']:
            has_rated = False
            user_rating = None
            if self.request.user.is_authenticated:
                has_rated = dish.user_has_rated(self.request.user)
                if has_rated:
                    user_rating = dish.get_user_rating(self.request.user)
            
            dishes_with_ratings.append({
                'dish': dish,
                'has_rated': has_rated,
                'user_rating': user_rating,
                'average_rating': dish.average_rating,
                'total_ratings': dish.total_ratings,
            })
        
        context['dishes_with_ratings'] = dishes_with_ratings
        # Categories for filter buttons
        context['categories'] = Category.objects.all().only('id', 'category_name')
        context['selected_category'] = self.request.GET.get('category') or self.request.GET.get('categories') or ''
        return context


class DishDetailView(DetailView):
    model = Menu
    template_name = 'dish_details.html'
    context_object_name = 'dish'
    pk_url_kwarg = "product_pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dish = self.get_object()


        has_rated = False
        user_rating = None
        if self.request.user.is_authenticated:
            has_rated = dish.user_has_rated(self.request.user)
            if has_rated:
                user_rating = dish.get_user_rating(self.request.user)
        
        context['has_rated'] = has_rated
        context['user_rating'] = user_rating
        context['average_rating'] = dish.average_rating
        context['total_ratings'] = dish.total_ratings
        context['rating_form'] = RatingForm()
        
        return context


class SubmitRatingView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    
    def post(self, request, dish_id):
        dish = get_object_or_404(Menu, id=dish_id)
        
        # აქვს თუ არა შეფასებული
        if dish.user_has_rated(request.user):
            return redirect('restaurant:dish', product_pk=dish_id)


        # თუ არ აქვს ამ if ბლოკს აამუშავებს და შეაფასებს
        rating_value = request.POST.get('rating')
        if not rating_value:
            return redirect('restaurant:dish', product_pk=dish_id)

        try:
            rating_obj = Rating.objects.create(
                user=request.user,
                dish=dish,
                rating=int(rating_value)
            )
            messages.success(request, f'Thank you for rating {dish.name} with {rating_value} stars!')
        except Exception as e:
            messages.error(request, f'Error submitting rating: {str(e)}')

        return redirect('restaurant:dish', product_pk=dish_id)




class OrderListView(LoginRequiredMixin, View):
    template_name = 'order.html'
    login_url = '/user/login/'



    def get(self, request):
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.total for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'cart': cart,
            'total': total
        }
        return render(request, self.template_name, context)


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart





class AddToCartView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/user/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, dish_id):
        return self.add_to_cart(request, dish_id)
    
    def post(self, request, dish_id):
        return self.add_to_cart(request, dish_id)
    
    def add_to_cart(self, request, dish_id):
        dish = get_object_or_404(Menu, id=dish_id)
        cart = get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            dish=dish,
            defaults={'price': dish.price}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{dish.name} added to cart!')
        return redirect('restaurant:menu')


class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/user/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        dish_name = cart_item.dish.name
        cart_item.delete()
        
        messages.success(request, f'{dish_name} removed from cart!')
        return redirect('restaurant:cart')


class UpdateCartView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/user/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        
        cart_item.save()
        return redirect('restaurant:cart')


class ConfirmOrderView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    
    def post(self, request):
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty!')
            return redirect('restaurant:cart')
        
        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=cart.total_price,
            status='pending'
        )
        
        # კალათაში გადმოაქ შეკვეთა
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                dish=cart_item.dish,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
        
        # წაშლა
        cart_items.delete()
        
        messages.success(request, f'Order #{order.id} confirmed! Thank you for your order.')
        return redirect('restaurant:menu')






















