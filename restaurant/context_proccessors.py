from restaurant.models import Restaurant, Category, Menu, Rating



def global_settings(request):
    restaurant_branch = Restaurant.objects.all()
    category = Category.objects.all()
    all_dish = Menu.objects.all().select_related('category',)
    rate = Rating.objects.all().select_related('user')


    most_viewed = all_dish.order_by('views')[:6]
    highest_rated = rate.order_by('rating')[:6]




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.queryset.count().select_related('category')
        return context


    # კონტექსტი გავატანოთ returnში
    return {'all_dish': all_dish, 'most_viewed': most_viewed, 'highest_rated': highest_rated, 'restaurant_branch': restaurant_branch, 'category': category}