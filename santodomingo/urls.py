from django.urls import path
from .views import dish_list, orders, update_order_status_view, order_detail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('dishes/', dish_list, name='dish_list'),
    path('orders/', orders, name='orders'),  # Unificado GET y POST
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update_status/', update_order_status_view, name='update_order_status'),
]