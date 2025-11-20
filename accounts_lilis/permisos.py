from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(*roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("accounts_lilis:login")

            if request.user.rol not in roles_permitidos:
                messages.error(request, "No tienes permisos para acceder a este módulo.")
                return redirect("mantenedores")

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator


def permisos_por_rol(user):
    rol = user.rol

    return {
        # Usuarios
        "usuarios_ver": rol == "ADMIN",
        "usuarios_crear": rol == "ADMIN",
        "usuarios_editar": rol == "ADMIN",
        "usuarios_eliminar": rol == "ADMIN",

        # Proveedores
        "proveedores_ver": rol in ["ADMIN", "OPER_COMPRAS", "AUDITOR"],
        "proveedores_crear": rol in ["ADMIN", "OPER_COMPRAS"],
        "proveedores_editar": rol in ["ADMIN", "OPER_COMPRAS"],
        "proveedores_eliminar": rol in ["ADMIN", "OPER_COMPRAS"],
        "proveedores_solo_lectura": rol == "AUDITOR",

        # Productos
        "productos_ver": rol in ["ADMIN", "OPER_COMPRAS", "OPER_INVENTARIO", "OPER_PRODUCCION", "OPER_VENTAS", "ANALISTA_FIN", "AUDITOR"],
        "productos_crear": rol in ["ADMIN", "OPER_COMPRAS", "OPER_INVENTARIO", "OPER_VENTAS"],
        "productos_editar": rol in ["ADMIN", "OPER_COMPRAS", "OPER_INVENTARIO", "OPER_VENTAS"],
        "productos_eliminar": rol == "ADMIN",

        # Inventario
        "inventario_ver": rol in ["ADMIN", "OPER_INVENTARIO", "AUDITOR"],
        "inventario_crear": rol in ["ADMIN", "OPER_INVENTARIO"],


        # Otros
        "solo_lectura": rol == "AUDITOR"
    }
