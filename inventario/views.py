from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from .models import MovimientoInventario
from .forms import MovimientoInventarioForm
from accounts_lilis.permisos import permisos_por_rol, role_required
from django.utils import timezone

@login_required
@role_required("ADMIN", "OPER_INVENTARIO", "AUDITOR")
def movimientos_listar(request):
    movimientos = MovimientoInventario.objects.select_related(
        "producto", "proveedor", "bodega_origen", "bodega_destino", "usuario"
    ).all()
    permisos = permisos_por_rol(request.user)
    return render(request, "mantenedores/inventario/movimientos_listar.html", {
        "movimientos": movimientos, "permisos": permisos,
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

            # --- LOG AUDITORÍA ---
            print(f"🚛 [AUDITORIA] Fecha: {timezone.now()} | Usuario: {request.user.username} | Acción: CREAR_MOVIMIENTO | ID: {movimiento.id} | Producto: {movimiento.producto.nombre} | Cant: {movimiento.cantidad}")
            # ---------------------

            messages.success(request, "✅ Movimiento de inventario registrado correctamente.")
            return redirect("inventario:movimientos_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = MovimientoInventarioForm()
    permisos = permisos_por_rol(request.user)
    return render(request, "mantenedores/inventario/movimiento_form.html", {
        "form": form, "permisos": permisos,
    })

@login_required
@role_required("ADMIN", "OPER_INVENTARIO")
def movimiento_editar(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    fecha_original = movimiento.fecha  
    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST, instance=movimiento)
        if form.is_valid():
            movimiento_editado = form.save(commit=False)
            movimiento_editado.fecha = fecha_original 
            movimiento_editado.save()

            # --- LOG AUDITORÍA ---
            print(f"📝 [AUDITORIA] Fecha: {timezone.now()} | Usuario: {request.user.username} | Acción: EDITAR_MOVIMIENTO | ID: {pk}")
            # ---------------------

            messages.success(request, "✅ Movimiento de inventario actualizado correctamente.")
            return redirect("inventario:movimientos_listar")
        messages.error(request, "❌ Revisa los errores del formulario.")
    else:
        form = MovimientoInventarioForm(instance=movimiento)
    permisos = permisos_por_rol(request.user)
    return render(request, "mantenedores/inventario/movimiento_form.html", {
        "form": form, "permisos": permisos,
    })

@login_required
@role_required("ADMIN", "OPER_INVENTARIO")
def movimiento_eliminar(request, pk):
    movimiento = get_object_or_404(MovimientoInventario, pk=pk)
    if request.method == "POST":
        
        # --- LOG AUDITORÍA ---
        print(f"❌ [AUDITORIA] Fecha: {timezone.now()} | Usuario: {request.user.username} | Acción: ELIMINAR_MOVIMIENTO | ID: {pk} | Tipo: {movimiento.tipo}")
        # ---------------------

        movimiento.delete()
        messages.success(request, "✅ Movimiento de inventario eliminado correctamente.")
        return redirect("inventario:movimientos_listar")
    permisos = permisos_por_rol(request.user)
    return render(request, "mantenedores/inventario/movimiento_confirmar_eliminar.html", {
        "movimiento": movimiento, "permisos": permisos,
    })

def exportar_movimientos_excel(request):
    from .models import MovimientoInventario 
    movimientos = (
        MovimientoInventario.objects
        .select_related("producto", "proveedor", "bodega_origen", "bodega_destino", "usuario")
        .order_by("-fecha")
    )   
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos"
    encabezados = [
        "ID", "Fecha registro", "Tipo", "Producto", "Proveedor (RUT/NIF)",
        "Bodega origen", "Bodega destino", "Cantidad", "Lote", "Serie",
        "Fecha vencimiento", "Documento referencia", "Motivo", "Observaciones", "Usuario",
    ]
    ws.append(encabezados)
    for m in movimientos:
        ws.append([
            m.id,
            m.fecha.strftime("%d-%m-%Y %H:%M") if m.fecha else "",
            m.get_tipo_display(),
            m.producto.nombre if m.producto else "",
            m.proveedor.rut_nif if m.proveedor else "",
            m.bodega_origen.nombre if m.bodega_origen else "",
            m.bodega_destino.nombre if m.bodega_destino else "",
            float(m.cantidad) if m.cantidad is not None else "",
            m.lote or "",
            m.serie or "",
            m.fecha_vencimiento.strftime("%d-%m-%Y") if m.fecha_vencimiento else "",
            m.doc_referencia or "", # <-- Corregido para evitar error
            m.motivo or "",
            m.observaciones or "",
            m.usuario.username if getattr(m, "usuario", None) else "",
        ])
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="movimientos_inventario.xlsx"'
    wb.save(response)
    return response