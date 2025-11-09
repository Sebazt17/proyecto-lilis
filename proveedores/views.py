from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Proveedor
from .forms import ProveedorForm

def tiene_permiso_proveedores(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS"]

@user_passes_test(tiene_permiso_proveedores)
@login_required
def mostrar_todos_proveedores(request):
    q = request.GET.get("q", "").strip()

    proveedores = Proveedor.objects.all().order_by("razon_social")

    if q:
        proveedores = proveedores.filter(
            Q(razon_social__icontains=q) |
            Q(rut_nif__icontains=q) |
            Q(email__icontains=q) |
            Q(ciudad__icontains=q)
        )

    context = {
        "proveedores": proveedores,   
    }
    return render(request, "mantenedores/proveedores/todos_proveedores.html", context)


@user_passes_test(tiene_permiso_proveedores)
@login_required
def crear_proveedor(request):
    form = ProveedorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("proveedores:listar")
    return render(request, "mantenedores/proveedores/MantenedorAgregarProveedor.html", {"form": form})

@user_passes_test(tiene_permiso_proveedores)
@login_required
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("proveedores:listar")
    return render(request, "mantenedores/proveedores/MantenedorEditarProveedor.html", {"form": form, "proveedor": proveedor})

@user_passes_test(lambda u: u.rol == "ADMIN")
@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        proveedor.delete()
        return JsonResponse({"ok": True})

    if request.method == "POST":
        proveedor.delete()
        return redirect("proveedores:listar")

    return redirect("proveedores:listar")

@user_passes_test(tiene_permiso_proveedores)
@login_required
def exportar_proveedores_excel(request):
    q = request.GET.get("q", "").strip()
    qs = Proveedor.objects.all().order_by("razon_social")
    if q:
        qs = qs.filter(
            Q(razon_social__icontains=q) |
            Q(rut_nif__icontains=q) |
            Q(email__icontains=q) |
            Q(ciudad__icontains=q)
        )

    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Proveedores"

    headers = [
        "RUT/NIF", "Razón Social", "Nombre Fantasía",
        "Email", "Teléfono", "Ciudad", "Región",
        "Dirección", "Sitio Web", "Moneda", "Condiciones Pago", "Estado"
    ]
    ws.append(headers)

    for p in qs:
        ws.append([
            p.rut_nif,
            p.razon_social,
            (p.nombre_fantasia or ""),
            p.email,
            (p.telefono or ""),
            (p.ciudad or ""),
            (p.region.nombre if getattr(p, "region", None) else ""),
            (p.direccion or ""),
            (p.sitio_web or ""),
            (p.moneda or ""),
            (p.condiciones_pago or ""),
            p.get_estado_display() if hasattr(p, "get_estado_display") else p.estado,
        ])

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                max_len = max(max_len, len(str(cell.value or "")))
            except:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 2, 45)

    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = 'attachment; filename="proveedores.xlsx"'
    wb.save(resp)
    return resp
