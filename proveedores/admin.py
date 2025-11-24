from django.contrib import admin
from proveedores.models import (
    Pais,
    DivisionAdministrativa,
    Proveedor,
    ProveedorProducto
)


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'codigo_iso']
    search_fields = ['nombre', 'codigo_iso']
    ordering = ['nombre']


@admin.register(DivisionAdministrativa)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'abreviacion', 'codigo_oficial', 'pais']
    search_fields = ['nombre', 'abreviacion', 'codigo_oficial']
    list_filter = ['pais']
    ordering = ['pais', 'nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'razon_social',
        'rut_nif',
        'email',
        'telefono',
        'pais',
        'division',
        'estado',
        'fecha_registro'
    ]
    list_filter = ['estado', 'pais', 'division']
    search_fields = ['razon_social', 'rut_nif', 'nombre_fantasia', 'email']
    ordering = ['razon_social']



@admin.register(ProveedorProducto)
class ProveedorProductoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'proveedor',
        'producto',
        'costo',
        'lead_time_dias',
        'preferente'
    ]
    list_filter = ['proveedor', 'preferente']
    search_fields = ['proveedor__razon_social', 'producto__nombre']
    ordering = ['proveedor']
