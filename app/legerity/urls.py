from django.urls import path
from rest_framework.routers import DefaultRouter
from legerity import views

router = DefaultRouter()
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')
# router.register(r'giftboxes', views.GiftBoxViewSet, basename='giftboxes')
# router.register(r'giftbox-items', views.GiftBoxItemViewSet,
# basename='giftbox-items')

urlpatterns = [
    path('about/', views.AboutListView.as_view(), name='about'),
    path('reviews/', views.ReviewListView.as_view(), name='reviews'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('checkout/', views.OrderView.as_view(), name='checkout'),
]

urlpatterns += router.urls
