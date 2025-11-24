from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Q

from .models import Proveedor, Pais, DivisionAdministrativa
from .forms import ProveedorForm
from .permisos import permisos_proveedores_context
from .choices import CONDICIONES_PAGO


# --------------------------
# VALIDACIONES DE ACCESO
# --------------------------

def puede_entrar_modulo(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS", "AUDITOR"]


def puede_crear(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS"]


def puede_editar(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS"]


def puede_eliminar(user):
    return user.is_authenticated and user.rol == "ADMIN"


# --------------------------
# LISTAR PROVEEDORES
# --------------------------

@login_required
@user_passes_test(puede_entrar_modulo)
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
        **permisos_proveedores_context(request.user),
    }
    return render(request, "mantenedores/proveedores/todos_proveedores.html", context)


# --------------------------
# CREAR PROVEEDOR
# --------------------------

@login_required
@user_passes_test(puede_crear)
def crear_proveedor(request):
    form = ProveedorForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("proveedores:listar")

    return render(
        request,
        "mantenedores/proveedores/MantenedorAgregarProveedor.html",
        {
            "form": form,
            **permisos_proveedores_context(request.user),
        }
    )


# --------------------------
# EDITAR PROVEEDOR
# --------------------------

@login_required
@user_passes_test(puede_editar)
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    form = ProveedorForm(request.POST or None, instance=proveedor)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("proveedores:listar")

    return render(
        request,
        "mantenedores/proveedores/MantenedorEditarProveedor.html",
        {
            "form": form,
            "proveedor": proveedor,
            **permisos_proveedores_context(request.user),
        }
    )


# --------------------------
# ELIMINAR PROVEEDOR
# --------------------------

@login_required
@user_passes_test(puede_eliminar)
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == "POST":
        proveedor.delete()
        return redirect("proveedores:listar")

    return redirect("proveedores:listar")


# --------------------------
# EXPORTAR A EXCEL
# --------------------------

@login_required
@user_passes_test(puede_entrar_modulo)
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

    wb = Workbook()
    ws = wb.active
    ws.title = "Proveedores"

    headers = [
        "RUT/NIF", "Razón Social", "Nombre Fantasía",
        "Email", "Teléfono", "Ciudad",
        "País", "División",
        "Dirección", "Sitio Web",
        "Moneda", "Condiciones Pago", "Estado"
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
            (p.pais.nombre if p.pais else ""),
            (p.division.nombre if p.division else ""),
            (p.direccion or ""),
            (p.sitio_web or ""),
            p.moneda,
            dict(CONDICIONES_PAGO).get(p.condiciones_pago, p.condiciones_pago),
            p.get_estado_display() if hasattr(p, "get_estado_display") else p.estado,
        ])

    from openpyxl.writer.excel import save_virtual_workbook
    respuesta = HttpResponse(
        save_virtual_workbook(wb),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    respuesta["Content-Disposition"] = 'attachment; filename=\"proveedores.xlsx\"'
    return respuesta


# --------------------------
# AJAX: OBTENER DIVISIONES POR PAÍS
# --------------------------

@login_required
@user_passes_test(puede_entrar_modulo)
def obtener_divisiones(request, pais_id):
    divisiones = DivisionAdministrativa.objects.filter(
        pais_id=pais_id
    ).order_by("nombre")
    data = [{"id": d.id, "nombre": d.nombre} for d in divisiones]
    return JsonResponse(data, safe=False)
