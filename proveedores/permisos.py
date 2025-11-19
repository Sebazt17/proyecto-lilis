def permisos_proveedores_context(user):
    rol = getattr(user, "rol", None)

    return {
        "proveedores_listar": rol in ["ADMIN", "OPER_COMPRAS", "AUDITOR"],
        "proveedores_crear": rol in ["ADMIN", "OPER_COMPRAS"],
        "proveedores_editar": rol in ["ADMIN", "OPER_COMPRAS"],
        "proveedores_eliminar": rol == "ADMIN",
    }
