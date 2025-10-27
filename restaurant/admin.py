from django.contrib import admin

from restaurant.models import Restaurant, Category, Menu


# Register your models here.
# admin.site.register([Restaurant, Category, Menu])




# Menu display
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')

    readonly_fields = ('views',)







@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description')




@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('branch', 'address')


