from rest_framework import serializers
from django.core.validators import RegexValidator
from legerity.models import About, Product, Review, CartItem, Cart, Order, OrderProduct
from customer.models import User

phone_number_validator = RegexValidator(
    regex=r'^(\+[0-9]{1,3})?[0-9]{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class AboutListSerializer(serializers.ModelSerializer):
    number_of_customers = serializers.SerializerMethodField()
    number_of_products = serializers.SerializerMethodField()

    class Meta:
        model = About
        fields = ['number_of_customers', 'number_of_products',
                  'number_of_personals', 'satisfaction_percent']

    def get_number_of_customers(self, obj):
        return User.objects.filter(is_staff=False).count()

    def get_number_of_products(self, obj):
        return Product.objects.count()


class ReviewListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['fullname', 'image', 'comment']


class ProductListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'info', 'price', 'image']

    def get_name(self, obj):
        return f'Legerity Beauty Hair {obj.category}'


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

    def validate(self, data):
        ''' Ensure stock availability before adding to cart.  '''
        product = data.get('product')
        quantity = data.get('quantity')

        if product and quantity > product.stock:
            raise serializers.ValidationError('Not enough stock')

        return data


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')

        return value


class CartItemListSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal_price']

    def get_subtotal_price(self, obj):
        return obj.product.price * obj.quantity


class CartListSerializer(serializers.ModelSerializer):
    cart_items = CartItemListSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['cart_items', 'total_price']

    def get_total_price(self, obj):
        total_price = sum(item.product.price *
                          item.quantity for item in obj.cart_items.all())
        return total_price


# class GiftBoxItemSerializer(serializers.ModelSerializer):
#     gift_box = serializers.PrimaryKeyRelatedField(
#         queryset=GiftBox.objects.all(), write_only=True
#     )

#     class Meta:
#         model = GiftBoxItem
#         fields = ['id', 'product', 'gift_box', 'quantity']


# class GiftBoxSerializer(serializers.ModelSerializer):
#     items = GiftBoxItemSerializer(
#         many=True, source='giftboxitem_set', read_only=True)

#     class Meta:
#         model = GiftBox
#         fields = ['id', 'name', 'items']


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderCreateSerializer(serializers.Serializer):
    # fullname = serializers.CharField(required=False)
    # email = serializers.EmailField(required=False)
    address = serializers.CharField()
    zip_code = serializers.CharField()
    phone_number = serializers.CharField(validators=[phone_number_validator])

    def validate(self, attrs):
        user = self.context['request'].user
        cart = getattr(user, 'cart', None)

        if not cart or not cart.cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart

        # fullname = validated_data.get('fullname', user.fullname)
        # email = validated_data.get('email', user.email)
        address = validated_data['address']
        zip_code = validated_data['zip_code']
        phone_number = validated_data['phone_number']

        total_price = sum([
            item.product.price * item.quantity
            for item in cart.cart_items.all()
        ])

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            address=address,
            zip_code=zip_code,
            phone_number=phone_number,
        )

        for item in cart.cart_items.all():
            OrderProduct.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )

        # Clear cart
        cart.cart_items.all().delete()

        return order
