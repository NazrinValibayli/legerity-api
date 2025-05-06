from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, extend_schema_view

from legerity.models import About, Review, Product, Cart, CartItem
from legerity.serializers import AboutListSerializer, ReviewListSerializer, ProductListSerializer, CartItemCreateSerializer, CartItemListSerializer, CartItemUpdateSerializer, CartListSerializer, OrderCreateSerializer

from django.db import transaction


class AboutListView(generics.ListAPIView):
    queryset = About.objects.all()
    serializer_class = AboutListSerializer


class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get Cart Items",
        description="Retrieve all items in the authenticated user's cart.",
        responses={200: CartItemListSerializer(many=True)}
    ),
    create=extend_schema(
        summary="Add Product to Cart",
        description="Add a new product to the cart. If the product is already in the cart, a 400 error is returned.",
        request=CartItemCreateSerializer,
        responses={201: CartItemListSerializer, 400: {
            "error": "Product already in cart. Use PATCH to update quantity."}}
    ),
    partial_update=extend_schema(
        summary="Update Cart Item Quantity",
        description="Update the quantity of an existing cart item. Only quantity updates are allowed.",
        request=CartItemUpdateSerializer,
        responses={200: CartItemListSerializer,
                   404: {"error": "Cart item not found"}}
    ),
    destroy=extend_schema(
        summary="Remove Product from Cart",
        description="Remove a product from the cart.",
        responses={204: None, 404: {"error": "Cart item not found"}}
    )
)
class CartItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        ''' Retrieve or create the cart for the authenticated user. '''
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        ''' Retrieve all products  in the user's cart. '''
        cart = self.get_cart(request)
        serializer = CartListSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        ''' Handle adding  a product to the cart (only new items, no quantity update). '''
        cart = self.get_cart(request)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id:
            return Response({'product': 'This field is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not quantity:
            return Response({'quantity': 'This field is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if item already exists in the cart
        if CartItem.objects.filter(cart=cart, product=product).exists():
            return Response({'error': 'Product already in cart. Use PATCH to update quantity'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartItem.objects.create(
            cart=cart, product=product, quantity=quantity)
        serializer = CartItemCreateSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        ''' Update the quantity of an existing cart item (PATCH request). '''
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if new_quantity is None:
            return Response({'error': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_quantity > cart_item.product.stock:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()
        serializer = CartItemUpdateSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        ''' Remove an item from the cart (DELETE request). '''
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


# class GiftBoxViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GiftBoxSerializer

#     def get_queryset(self):
#         return GiftBox.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class GiftBoxItemViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GiftBoxItemSerializer

#     def get_queryset(self):
#         return GiftBoxItem.objects.filter(gift_box__user=self.request.user)

#     def perform_create(self, serializer):
#         gift_box_id = self.request.data.get('gift_box')
#         try:
#             gift_box = GiftBox.objects.get(
#                 id=gift_box_id, user=self.request.user)
#         except GiftBox.DoesNotExist:
#             raise serializer.ValidationError('Gift box not found.')

#         serializer.save(gift_box_id=gift_box_id)


class OrderView(generics.GenericAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({'message': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)
