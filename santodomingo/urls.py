from django.urls import path
from .views import lista_platos, pedidos, actualizar_estado_pedido, detalle_pedido
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('platos/', lista_platos, name='lista_platos'),
    path('pedidos/', pedidos, name='pedidos'),  # Unificado GET y POST
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('pedidos/<int:pedido_id>/', detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/actualizar_estado/', actualizar_estado_pedido, name='actualizar_estado_pedido'),
]