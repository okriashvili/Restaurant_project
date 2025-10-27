from django.contrib.auth.models import User
from django.db import models


# კალათის მოდელი
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.id} (Session)"

    @property
    def total_price(self):
        return sum(item.total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey('Menu', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('cart', 'dish')

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

    @property
    def total(self):
        return self.quantity * self.price


# რესტორნების ქსელი
class Restaurant(models.Model):
    branch = models.CharField(max_length=50)
    address = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'Restarunat_branch'
        verbose_name_plural = 'Restarunat'


    def __str__(self):
        return self.branch



# კატეგორიის მოდელი
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name



# კერძების მოდელი
class Menu(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dish')
    branch = models.ManyToManyField(Restaurant, related_name='menu_items')
    image = models.ImageField(upload_to='dish_image/', null=True, blank=True)
    available = models.BooleanField(default=True)
    spiciness = models.IntegerField(choices= [
    (0, 'No spicy'),
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'Hot'),
    (4, 'Very Hot')], blank=True)
    is_gluten_free = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        help_text="Rate this dish from 1 to 5 stars", null=True, blank=True
        )
    views = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        from django.db.models import Avg
        avg = self.ratings.all().aggregate(Avg('rating'))['rating__avg']
        if avg:
            return round(avg, 2)
        return 0

    @property
    def total_ratings(self):
        return self.ratings.count()

    def user_has_rated(self, user):
        if not user.is_authenticated:
            return False
        return self.ratings.filter(user=user).exists()

    def get_user_rating(self, user):
        if not user.is_authenticated:
            return None
        rating_obj = self.ratings.filter(user=user).first()
        if rating_obj:
            return rating_obj.rating
        return None



# მომხმარებლის შეკვეთის მოდული
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey('Menu', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'OrderItem'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

    @property
    def total(self):
        return self.quantity * self.price




class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ('user', 'dish')  # Ensures user can only rate once per dish

    def __str__(self):
        return f"{self.user.username} rated {self.dish.name} {self.rating} stars"

