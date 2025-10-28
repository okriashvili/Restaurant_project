from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from restaurant.models import Menu


class DishCountMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        resolver = resolve(request.path_info)

        if resolver.view_name == 'restaurant:dish':
            product_pk = view_kwargs.get('product_pk')

            if product_pk:
                Dish = Menu.objects.get(pk=product_pk)

                Dish.views += 1
                Dish.save(update_fields=['views'])

    def process_request(self, request):
        print('hello world')

    def process_response(self, request, response):
        return response








