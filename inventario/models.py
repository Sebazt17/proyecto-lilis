from django.db import models
from django.utils import timezone

from catalogo.models import Producto
from proveedores.models import Proveedor
from accounts_lilis.models import Usuario


class Bodega(models.Model):
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código Bodega")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Bodega")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        db_table = "bodega"
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"
        ordering = ["codigo"]


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = (
        ("INGRESO", "Ingreso"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste"),
        ("DEVOLUCION", "Devolución"),
        ("TRANSFERENCIA", "Transferencia"),
    )

    tipo = models.CharField(
        max_length=15,
        choices=TIPO_MOVIMIENTO,
        verbose_name="Tipo de movimiento"
    )
    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha")

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="movimientos",
        verbose_name="Producto"
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos",
        verbose_name="Proveedor"
    )

    bodega_origen = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos_salida",
        verbose_name="Bodega origen"
    )
    bodega_destino = models.ForeignKey(
        Bodega,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimientos_ingreso",
        verbose_name="Bodega destino"
    )

    cantidad = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        verbose_name="Cantidad"
    )

    lote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Lote"
    )
    serie = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Serie"
    )
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de vencimiento"
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="movimientos_registrados",
        verbose_name="Registrado por"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        db_table = "movimiento_inventario"
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ["-fecha"]     