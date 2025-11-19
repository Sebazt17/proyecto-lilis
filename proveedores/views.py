from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Proveedor
from .forms import ProveedorForm
from .permisos import permisos_proveedores_context

# -------- VALIDACIONES DE ACCESO -------- #

def puede_entrar_modulo(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS", "AUDITOR"]

def puede_crear(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS"]

def puede_editar(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_COMPRAS"]

def puede_eliminar(user):
    return user.is_authenticated and user.rol == "ADMIN"


# -------- VISTAS -------- #

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


@login_required
@user_passes_test(puede_eliminar)
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == "POST":
        proveedor.delete()
        return redirect("proveedores:listar")

    return redirect("proveedores:listar")


@login_required
@user_passes_test(puede_entrar_modulo)
def exportar_proveedores_excel(request):
    # Auditor puede exportar, no es "creación"
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

    from openpyxl.writer.excel import save_virtual_workbook
    respuesta = HttpResponse(
        save_virtual_workbook(wb),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    respuesta["Content-Disposition"] = 'attachment; filename="proveedores.xlsx"'
    return respuesta
