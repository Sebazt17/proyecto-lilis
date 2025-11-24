from django.urls import path
from . import views

app_name = "proveedores"

urlpatterns = [
    path("", views.mostrar_todos_proveedores, name="listar"),
    path("agregar/", views.crear_proveedor, name="agregar"),
    path("editar/<int:id>/", views.editar_proveedor, name="editar"),
    path("eliminar/<int:id>/", views.eliminar_proveedor, name="eliminar"),

    path("exportar/", views.exportar_proveedores_excel, name="exportar"),

    path(
        "divisiones/<int:pais_id>/",
        views.obtener_divisiones,
        name="obtener_divisiones"
    ),
]
