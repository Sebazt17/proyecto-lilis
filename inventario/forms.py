from datetime import date
from django import forms
from .models import MovimientoInventario


class MovimientoInventarioForm(forms.ModelForm):
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
        widgets = {
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
            "cantidad": forms.NumberInput(
                attrs={
                    "min": "1",
                    "step": "1",   
                }
            ),
        }

    def clean_cantidad(self):
        """
        Valida que la cantidad sea un número entero positivo (sin decimales).
        """
        cantidad = self.cleaned_data.get("cantidad")

        if cantidad is None:
            return cantidad

        if cantidad != int(cantidad):
            raise forms.ValidationError(
                "La cantidad debe ser un número entero (sin decimales)."
            )

        if cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        # Devolvemos el entero (Django lo adapta al tipo del campo del modelo)
        return int(cantidad)

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        bodega_origen = cleaned_data.get("bodega_origen")
        bodega_destino = cleaned_data.get("bodega_destino")
        fecha_venc = cleaned_data.get("fecha_vencimiento")


        # Validaciones simples según tipo

        if fecha_venc:
            if fecha_venc < date.today():
                raise forms.ValidationError(
                    "La fecha de vencimiento no puede ser menor a la fecha actual."
                )


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
