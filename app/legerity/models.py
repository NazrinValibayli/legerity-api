from django.db import models
from django.forms import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

# Create your models here.


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError(
                'There can be only one %s instance' % self.__class__.__name__)
        return super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create()
        return obj


class About(SingletonModel):
    number_of_personals = models.IntegerField(_('Number of Personals'))
    satisfaction_percent = models.IntegerField(_('Satisfaction Percent'))

    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return 'About'


class Review(models.Model):
    fullname = models.CharField(_('Fullname'), max_length=100)
    image = models.ImageField(_('Reviewer Image'), upload_to='reviews')
    comment = HTMLField(_('Comment'))

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def __str__(self):
        return f'Review by {self.fullname}'


class Product(models.Model):
    class Category(models.TextChoices):
        mask = 'Mask', _('Mask')
        balm = 'Balm', _('Balm')
        cream = 'Cream', _('Cream')
        oil = 'Oil', _('Oil')
        shampoo = 'Shampoo', _('Shampoo')

    info = HTMLField(_('Info'))
    price = models.DecimalField(
        _('Price'), max_digits=10, decimal_places=2, db_index=True)
    stock = models.IntegerField(_('Stock'), db_index=True)
    image = models.ImageField(_('Product Image'), upload_to='products')
    category = models.CharField(
        _('Category'), max_length=100, choices=Category.choices, db_index=True)
    sales_number = models.IntegerField(
        _('Sales Number'), db_index=True, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['price'], name='price'),
            models.Index(fields=['stock'], name='stock'),
            models.Index(fields=['category'], name='category'),
            models.Index(fields=['sales_number'], name='sales_number'),
        ]

    def __str__(self):
        return f'{self.category}: {self.price}'


class Cart(models.Model):
    user = models.OneToOneField(
        'customer.User', verbose_name=_('User'), on_delete=models.CASCADE, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='user-cart'),
        ]

    def __str__(self):
        return f'{self.user}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_(
        'Cart'), on_delete=models.CASCADE, db_index=True, related_name='cart_items')
    product = models.ForeignKey(Product, verbose_name=_(
        'Product'), on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(_('Quantity'))

    class Meta:
        indexes = [
            models.Index(fields=['cart'], name='cart'),
        ]

    def __str__(self):
        return f'{self.cart}: {self.product}-{self.quantity}'


# class GiftBox(models.Model):
#     user = models.ForeignKey('customer.User', verbose_name=_(
#         'User'), on_delete=models.CASCADE, db_index=True)
#     name = models.CharField(_('Name'), max_length=100, db_index=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['user'], name='user-gift-box'),
#             models.Index(fields=['user', 'name'], name='user&name')
#         ]

#     def __str__(self):
#         return f'{self.user}: {self.name}'


# class GiftBoxItem(models.Model):
#     gift_box = models.ForeignKey(GiftBox, verbose_name=_(
#         'Gift Box'), on_delete=models.CASCADE, db_index=True)
#     product = models.ForeignKey(Product, verbose_name=_('Product'),
#                                 on_delete=models.SET_NULL, null=True)
#     quantity = models.IntegerField(_('Quantity'))

#     class Meta:
#         indexes = [
#             models.Index(fields=['gift_box'], name='gift_box'),
#         ]

#     def __str__(self):
#         return f'{self.gift_box} - {self.product}'


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        prepared = 'Prepared', _('Prepared')
        delivered = 'Delivered', _('Delivered')
        canceled = 'Canceled', _('Canceled')

    phone_number_regex = RegexValidator(
        regex=r'^(\+[0-9]{1,3})?[0-9]{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    user = models.ForeignKey('customer.User', verbose_name=_(
        'User'), on_delete=models.CASCADE)
    total_price = models.DecimalField(
        _('Total Price'), max_digits=10, decimal_places=2)
    status = models.CharField(_('Status'),
                              max_length=10, choices=OrderStatus.choices, default=OrderStatus.prepared)
    address = models.CharField(_('Address'), max_length=255)
    zip_code = models.CharField(_('Zip Code'), max_length=50)
    phone_number = models.CharField(_('Phone'),
                                    max_length=20, validators=[phone_number_regex])
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='user_index'),
            models.Index(fields=['phone_number'], name='phone_index'),
            models.Index(fields=['status'], name='status_index')
        ]

    def __str__(self):
        return f'Checkout #{self.id} by {self.user}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, verbose_name=_('Order'), related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_(
        'Product'), on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(_('Quantity'))

    class Meta:
        indexes = [
            models.Index(fields=['order'], name='order_index')
        ]

    def __str__(self):
        return f'{self.order} - {self.product}'


# class OrderGiftBox(models.Model):
#     order = models.ForeignKey(
#         Order, related_name='giftboxes', on_delete=models.CASCADE)
#     gift_box = models.ForeignKey(GiftBox, on_delete=models.SET_NULL, null=True)

#     def __str__(self):
#         return f'{self.order} - {self.gift_box}'
