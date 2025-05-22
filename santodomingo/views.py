from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Plato, Pedido, ItemPedido, Cliente
import json

# API para listar platos (sin autenticación)
@api_view(['GET'])
def lista_platos(request):
    platos = Plato.objects.all()
    data = [{
        'id': plato.id,
        'nombre': plato.nombre,
        'categoria': plato.categoria,
        'descripcion': plato.descripcion,
        'precio': str(plato.precio),
        'url_imagen': plato.url_imagen
    } for plato in platos]
    return JsonResponse(data, safe=False)

# API para crear pedidos (sin autenticación)
@csrf_exempt
@api_view(['POST'])
def crear_pedido(request):
    try:
        data = json.loads(request.body)
        nombre_cliente = data.get('nombre_cliente')
        telefono_cliente = data.get('telefono_cliente')
        direccion_cliente = data.get('direccion_cliente')
        items = data.get('items')  # Lista de {'plato_id': id, 'cantidad': qty}

        if not all([nombre_cliente, telefono_cliente, direccion_cliente, items]):
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

        # Buscar o crear cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre_cliente,
            telefono=telefono_cliente,
            direccion=direccion_cliente
        )

        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=cliente,
            precio_total=0
        )

        # Añadir ítems y calcular total
        precio_total = 0
        for item in items:
            plato = Plato.objects.get(id=item['plato_id'])
            cantidad = item['cantidad']
            ItemPedido.objects.create(
                pedido=pedido,
                plato=plato,
                cantidad=cantidad
            )
            precio_total += plato.precio * cantidad

        pedido.precio_total = precio_total
        pedido.save()

        return JsonResponse({'mensaje': 'Pedido creado', 'pedido_id': pedido.id})
    except Plato.DoesNotExist:
        return JsonResponse({'error': 'Plato no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para listar y crear pedidos (sin autenticación)
@csrf_exempt
@api_view(['GET', 'POST'])
def pedidos(request):
    if request.method == 'GET':
        pedidos = Pedido.objects.all().order_by('-id')
        estado = request.GET.get('estado')
        nombre_cliente = request.GET.get('nombre_cliente')
        cliente_id = request.GET.get('cliente_id')

        if estado:
            pedidos = pedidos.filter(estado=estado)
        if nombre_cliente:
            pedidos = pedidos.filter(cliente__nombre__icontains=nombre_cliente)
            if not pedidos.exists():
                return JsonResponse({'error': f'No se encontraron pedidos para el cliente "{nombre_cliente}".'}, status=404)
        if cliente_id:
            pedidos = pedidos.filter(cliente__id=cliente_id)
            if not pedidos.exists():
                return JsonResponse({'error': f'No se encontraron pedidos para el cliente con ID {cliente_id}.'}, status=404)

        data = []
        for pedido in pedidos:
            items = ItemPedido.objects.filter(pedido=pedido).select_related('plato')
            items_data = [{
                'plato_id': item.plato.id,
                'plato_nombre': item.plato.nombre,
                'cantidad': item.cantidad,
                'precio': str(item.plato.precio)
            } for item in items]
            data.append({
                'pedido_id': pedido.id,
                'nombre_cliente': pedido.cliente.nombre,
                'telefono_cliente': pedido.cliente.telefono,
                'direccion_cliente': pedido.cliente.direccion,
                'estado': pedido.estado,
                'creado_en': pedido.creado_en.isoformat(),
                'precio_total': str(pedido.precio_total),
                'items': items_data
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre_cliente = data.get('nombre_cliente')
            telefono_cliente = data.get('telefono_cliente')
            direccion_cliente = data.get('direccion_cliente')
            items = data.get('items')  # Lista de {'plato_id': id, 'cantidad': qty}

            if not all([nombre_cliente, telefono_cliente, direccion_cliente, items]):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

            # Buscar o crear cliente
            cliente, created = Cliente.objects.get_or_create(
                nombre=nombre_cliente,
                telefono=telefono_cliente,
                direccion=direccion_cliente
            )

            # Crear el pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                precio_total=0
            )

            # Añadir ítems y calcular total
            precio_total = 0
            for item in items:
                plato = Plato.objects.get(id=item['plato_id'])
                cantidad = item['cantidad']
                ItemPedido.objects.create(
                    pedido=pedido,
                    plato=plato,
                    cantidad=cantidad
                )
                precio_total += plato.precio * cantidad

            pedido.precio_total = precio_total
            pedido.save()

            return JsonResponse({'mensaje': 'Pedido creado', 'pedido_id': pedido.id})
        except Plato.DoesNotExist:
            return JsonResponse({'error': 'Plato no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

# API para obtener un pedido específico por ID (sin autenticación)
@api_view(['GET'])
def detalle_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        items = ItemPedido.objects.filter(pedido=pedido).select_related('plato')
        items_data = [{
            'plato_id': item.plato.id,
            'plato_nombre': item.plato.nombre,
            'cantidad': item.cantidad,
            'precio': str(item.plato.precio)
        } for item in items]
        data = {
            'pedido_id': pedido.id,
            'nombre_cliente': pedido.cliente.nombre,
            'telefono_cliente': pedido.cliente.telefono,
            'direccion_cliente': pedido.cliente.direccion,
            'estado': pedido.estado,
            'creado_en': pedido.creado_en.isoformat(),
            'precio_total': str(pedido.precio_total),
            'items': items_data
        }
        return JsonResponse(data)
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# API para actualizar estado de pedidos (con autenticación JWT)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def actualizar_estado_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        data = json.loads(request.body)
        estado = data.get('estado')
        if estado not in ['pendiente', 'atendido']:
            return JsonResponse({'error': 'Estado inválido'}, status=400)
        pedido.estado = estado
        pedido.save()
        return JsonResponse({'mensaje': 'Estado actualizado'})
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)