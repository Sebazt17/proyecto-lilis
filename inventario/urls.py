from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("movimientos/", views.movimientos_listar, name="movimientos_listar"),
    path("movimientos/nuevo/", views.movimiento_crear, name="movimiento_crear"),
    path("movimientos/<int:pk>/editar/", views.movimiento_editar, name="movimiento_editar"),
    path("movimientos/<int:pk>/eliminar/", views.movimiento_eliminar, name="movimiento_eliminar"),
]
