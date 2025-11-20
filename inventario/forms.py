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
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        bodega_origen = cleaned_data.get("bodega_origen")
        bodega_destino = cleaned_data.get("bodega_destino")

        # Validaciones simples según tipo (puedes sofisticar esto después)
        if tipo == "TRANSFERENCIA":
            if not bodega_origen or not bodega_destino:
                raise forms.ValidationError("Para una transferencia debes indicar bodega origen y destino.")
            if bodega_origen == bodega_destino:
                raise forms.ValidationError("La bodega origen y destino no pueden ser la misma.")
        elif tipo == "INGRESO":
            if not bodega_destino:
                raise forms.ValidationError("Para un ingreso debes indicar la bodega destino.")
        elif tipo in ["SALIDA", "DEVOLUCION"]:
            if not bodega_origen:
                raise forms.ValidationError(f"Para una {tipo.lower()} debes indicar la bodega origen.")

        return cleaned_data
