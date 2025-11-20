from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MovimientoInventario, Bodega
from .forms import MovimientoInventarioForm
from accounts_lilis.permisos import permisos_por_rol, role_required


@login_required
@role_required("ADMIN", "OPER_INVENTARIO", "AUDITOR")
def movimientos_listar(request):
    movimientos = MovimientoInventario.objects.select_related(
        "producto", "proveedor", "bodega_origen", "bodega_destino", "usuario"
    ).all()

    permisos = permisos_por_rol(request.user.rol)
    return render(request, "mantenedores/inventario/movimientos_listar.html", {
        "movimientos": movimientos,
        "permisos": permisos,
    })


@login_required
@role_required("ADMIN", "OPER_INVENTARIO")
def movimiento_crear(request):
    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            messages.success(request, "✅ Movimiento de inventario registrado correctamente.")
            return redirect("inventario:movimientos_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = MovimientoInventarioForm()

    permisos = permisos_por_rol(request.user.rol)
    return render(request, "mantenedores/inventario/movimiento_form.html", {
        "form": form,
        "permisos": permisos,
    })
