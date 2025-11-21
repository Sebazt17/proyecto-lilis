from django import forms
from django.utils import timezone
from .models import MovimientoInventario


class MovimientoInventarioForm(forms.ModelForm):
    # 👇 Campo cantidad: solo enteros positivos
    cantidad = forms.DecimalField(
        min_value=1,
        max_digits=12,
        decimal_places=0,
        label="Cantidad",
        error_messages={
            "min_value": "La cantidad debe ser un número entero mayor a cero.",
            "invalid": "La cantidad debe ser un número entero.",
        },
    )

    # 👇 Lote obligatorio, con rango de longitud
    lote = forms.CharField(
        required=True,
        min_length=3,
        max_length=30,
        label="Lote",
        error_messages={
            "required": "El lote es obligatorio.",
            "min_length": "El lote debe tener al menos 3 caracteres.",
            "max_length": "El lote no puede superar los 30 caracteres.",
        },
    )

    # 👇 Serie obligatoria, con rango de longitud
    serie = forms.CharField(
        required=True,
        min_length=3,
        max_length=30,
        label="Serie",
        error_messages={
            "required": "La serie es obligatoria.",
            "min_length": "La serie debe tener al menos 3 caracteres.",
            "max_length": "La serie no puede superar los 30 caracteres.",
        },
    )

    # 👇 Observaciones obligatorias, con rango de longitud
    observaciones = forms.CharField(
        required=True,
        min_length=5,
        max_length=300,
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": 300}),
        error_messages={
            "required": "Las observaciones son obligatorias.",
            "min_length": "Las observaciones deben tener al menos 5 caracteres.",
            "max_length": "Las observaciones no pueden superar los 300 caracteres.",
        },
    )

    # 👇 Fecha de vencimiento obligatoria
    fecha_vencimiento = forms.DateField(
        required=True,
        label="Fecha de vencimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
        error_messages={
            "required": "La fecha de vencimiento es obligatoria.",
            "invalid": "Ingresa una fecha de vencimiento válida.",
        },
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            "tipo",
            "producto",
            "proveedor",
            "bodega_origen",
            "bodega_destino",
            "cantidad",
            "lote",
            "serie",
            "fecha_vencimiento",
            "observaciones",
        ]

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get("fecha_vencimiento")
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError(
                "La fecha de vencimiento no puede ser anterior a hoy."
            )
        return fecha

    def clean(self):
        """
        Validaciones de coherencia según el tipo de movimiento
        (Ingreso, Salida, Transferencia, Devolución).
        """
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        bodega_origen = cleaned_data.get("bodega_origen")
        bodega_destino = cleaned_data.get("bodega_destino")

        # Reglas por tipo de movimiento (según requerimientos)
        if tipo == "TRANSFERENCIA":
            if not bodega_origen or not bodega_destino:
                raise forms.ValidationError(
                    "Para una transferencia debes indicar bodega origen y destino."
                )
            if bodega_origen == bodega_destino:
                raise forms.ValidationError(
                    "La bodega origen y destino no pueden ser la misma."
                )

        elif tipo == "INGRESO":
            if not bodega_destino:
                raise forms.ValidationError(
                    "Para un ingreso debes indicar la bodega destino."
                )

        elif tipo in ["SALIDA", "DEVOLUCION"]:
            if not bodega_origen:
                raise forms.ValidationError(
                    f"Para una {tipo.lower()} debes indicar la bodega origen."
                )

        return cleaned_data
