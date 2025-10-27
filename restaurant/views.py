from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    ListView, DetailView, TemplateView,
    RedirectView, View, UpdateView, DeleteView
)


from restaurant.models import Restaurant, Menu, Category, Order, OrderItem


# მთავარი გვერდი
class IndexView(TemplateView):
    template_name = 'index.html'
    context_object_name = 'batumi_branch, tbilisi_branch'




# კერძების ჩამონათვალი
class MenuListView(ListView):
    model = Menu
    template_name = 'menu.html'
    context_object_name = 'all_dish'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        # სერჩ ბარი
        search_query = self.request.GET.get('search')
        # სიცხარე
        spiciness_filter = self.request.GET.get('spiciness')
        # ვეჯი
        vegetarian_filter = self.request.GET.get('vegetarian')
        # ლაქტოზა
        gluten_free_filter = self.request.GET.get('gluten_free')

        # კატეგორიის მიხედვით
        categories_filter = self.request.GET.get('categories')



        if search_query:
            queryset = queryset.filter(Q(name__istartswith=search_query))

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


class DishDetailView(DetailView):
    model = Menu
    template_name = 'dish_details.html'
    context_object_name = 'dish'
    pk_url_kwarg = "product_pk"






class CartView(LoginRequiredMixin, View):
    template_name = 'order.html'

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, status='pending')
            items = order.items.all()
            total = order.total_price
        except Order.DoesNotExist:
            items = []
            total = 0

        return render(request, self.template_name, {'items': items, 'total': total})

    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, status='pending')
        except Order.DoesNotExist:
            return redirect('restaurant:order')

        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        item = get_object_or_404(OrderItem, id=item_id, order=order)

        if action == 'update':
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity > 0:
                item.quantity = new_quantity
                item.save()
            else:
                item.delete()
        elif action == 'delete':
            item.delete()

        order.total_price = sum(i.total for i in order.items.all())
        order.save()

        return redirect('restaurant:order')



class CartuUpdate(UpdateView):
    pass


class CartuDelete(DeleteView):
    pass







