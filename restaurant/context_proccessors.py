from restaurant.models import Restaurant, Category, Menu



def global_settings(request):
    restaurant_branch = Restaurant.objects.all()
    category = Category.objects.all()
    all_dish = Menu.objects.all().select_related('category',)


    most_viewed = all_dish.order_by('views')[:6]
    highest_rated = all_dish.order_by('rating')[:6]


    # spiciness = all_dish.get()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.queryset.count()
        return context


    # კონტექსტი გავატანოთ returnში
    return {'all_dish': all_dish, 'most_viewed': most_viewed, 'highest_rated': highest_rated, 'restaurant_branch': restaurant_branch, 'category': category}