from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Dish, Order, OrderItem
import json

# API para listar platos (sin autenticación)
def dish_list(request):
    if request.method == 'GET':
        dishes = Dish.objects.all()
        data = [{
            'id': dish.id,
            'name': dish.name,
            'category': dish.category,
            'description': dish.description,
            'price': str(dish.price),
            'image_url': settings.STATIC_URL + dish.image_url if dish.image_url else ''
        } for dish in dishes]
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# API para crear pedidos (sin autenticación)
@csrf_exempt
def create_order(request):
    if request.method == 'POST':
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
    return JsonResponse({'error': 'Solo se permite POST'}, status=405)

# Vista para listar pedidos (con autenticación, para staff)
@login_required
def order_list_view(request):
    orders = Order.objects.all()
    status = request.GET.get('status')
    customer_name = request.GET.get('customer_name')
    if status:
        orders = orders.filter(status=status)
    if customer_name:
        orders = orders.filter(customer_name__icontains=customer_name)
    context = {'orders': orders}
    return render(request, 'staff/order_list.html', context)

# Vista para actualizar estado de pedidos (con autenticación)
@login_required
def update_order_status_view(request, order_id):
    if request.method == 'POST':
        try:
            status = request.POST.get('status')
            if status not in ['pending', 'attended']:
                return JsonResponse({'error': 'Estado inválido'}, status=400)
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
            return redirect('order_list')
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Solo se permite POST'}, status=405)