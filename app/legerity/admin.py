from django.contrib import admin
from django.contrib.auth.models import Group
from legerity.models import About, Review, Product, Cart, CartItem, Order, OrderProduct
# Register your models here.
admin.site.site_header = 'Admin'

admin.site.register(About)
admin.site.register(Review)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
# admin.site.register(GiftBox)
# admin.site.register(GiftBoxItem)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status',)


admin.site.register(OrderProduct)
# admin.site.register(OrderGiftBox)

admin.site.unregister(Group)
