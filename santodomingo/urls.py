from django.urls import path
from .views import dish_list, create_order, order_list_view, update_order_status_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('dishes/', dish_list, name='dish_list'),
    path('orders/', create_order, name='create_order'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('staff/orders/', order_list_view, name='order_list'),
    path('staff/orders/<int:order_id>/update_status/', update_order_status_view, name='update_order_status'),
]