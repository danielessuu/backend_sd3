from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Dish, Order, OrderItem
import json

# API para listar platos (sin autenticación)
@api_view(['GET'])
def dish_list(request):
    dishes = Dish.objects.all()
    data = [{
        'id': dish.id,
        'name': dish.name,
        'category': dish.category,
        'description': dish.description,
        'price': str(dish.price),
        'image_url': dish.image_url
    } for dish in dishes]
    return JsonResponse(data, safe=False)

# API para crear pedidos (sin autenticación)
@csrf_exempt
@api_view(['POST'])
def create_order(request):
    try:
        data = json.loads(request.body)
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        customer_address = data.get('customer_address')
        items = data.get('items')  # Lista de {'dish_id': id, 'quantity': qty}

        if not all([customer_name, customer_phone, customer_address, items]):
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

        # Crear el pedido
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_price=0
        )

        # Añadir ítems y calcular total
        total_price = 0
        for item in items:
            dish = Dish.objects.get(id=item['dish_id'])
            quantity = item['quantity']
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=quantity
            )
            total_price += dish.price * quantity

        order.total_price = total_price
        order.save()

        return JsonResponse({'message': 'Pedido creado', 'order_id': order.id})
    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Plato no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para listar pedidos con ítems (con autenticación JWT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_with_items(request):
    if request.method == 'GET':
        orders = Order.objects.all().order_by('-id')
        status = request.GET.get('status')
        customer_name = request.GET.get('customer_name')
        if status:
            orders = orders.filter(status=status)
        if customer_name:
            orders = orders.filter(customer_name__icontains=customer_name)
        
        data = []
        for order in orders:
            items = OrderItem.objects.filter(order=order).select_related('dish')
            items_data = [{
                'dish_id': item.dish.id,
                'dish_name': item.dish.name,
                'quantity': item.quantity,
                'price': str(item.dish.price)
            } for item in items]
            data.append({
                'order_id': order.id,
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'customer_address': order.customer_address,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'total_price': str(order.total_price),
                'items': items_data
            })
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# API para actualizar estado de pedidos (con autenticación JWT)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def update_order_status_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        data = json.loads(request.body)
        status = data.get('status')
        if status not in ['pending', 'attended']:
            return JsonResponse({'error': 'Estado inválido'}, status=400)
        order.status = status
        order.save()
        return JsonResponse({'message': 'Estado actualizado'})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)