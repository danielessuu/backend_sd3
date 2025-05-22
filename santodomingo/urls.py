from django.urls import path
from .views import dish_list, create_order, order_list_view, update_order_status_view
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('dishes/', dish_list, name='dish_list'),
    path('orders/', create_order, name='create_order'),
    path('staff/login/', LoginView.as_view(template_name='staff/login.html'), name='login'),
    path('staff/logout/', LogoutView.as_view(), name='logout'),
    path('staff/orders/', order_list_view, name='order_list'),
    path('staff/orders/<int:order_id>/update_status/', update_order_status_view, name='update_order_status'),
]
