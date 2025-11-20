from django.contrib import admin
from .models import Bodega, MovimientoInventario


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "descripcion")
    search_fields = ("codigo", "nombre")
    ordering = ("codigo",)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "tipo",
        "producto",
        "proveedor",
        "bodega_origen",
        "bodega_destino",
        "cantidad",
        "usuario",
    )
    list_filter = (
        "tipo",
        "bodega_origen",
        "bodega_destino",
        "producto",
        "proveedor",
        "fecha",
    )
    search_fields = (
        "producto__nombre",
        "proveedor__nombre",
        "bodega_origen__nombre",
        "bodega_destino__nombre",
        "lote",
        "serie",
        "usuario__username",
    )
    date_hierarchy = "fecha"
    ordering = ("-fecha",)

    readonly_fields = ("fecha",)

    def save_model(self, request, obj, form, change):
        if not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
