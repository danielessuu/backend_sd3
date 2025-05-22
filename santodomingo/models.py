from django.db import models

class Dish(models.Model):
    name = models.CharField(max_length=100)  # Nombre del plato
    category = models.CharField(max_length=50)  # Categoría (ej. Entradas)
    description = models.TextField()  # Descripción del plato
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Precio con 2 decimales
    image_url = models.URLField()  # URL de la imagen (no subiremos archivos por simplicidad)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer_name = models.CharField(max_length=100)  # Nombre del cliente
    customer_phone = models.CharField(max_length=20)  # Teléfono del cliente
    customer_address = models.TextField()  # Dirección del cliente
    total_price = models.DecimalField(max_digits=8, decimal_places=2)  # Precio total
    status = models.CharField(max_length=20, default='pending')  # Estado: pending o attended
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de actualización

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Relación con Order
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)  # Relación con Dish
    quantity = models.PositiveIntegerField()  # Cantidad de este plato en el pedido

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"
