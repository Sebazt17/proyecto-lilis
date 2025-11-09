from django.shortcuts import render, get_object_or_404, redirect
from catalogo.models import Categoria, Producto
from catalogo.forms import ProductoForm
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from proveedores.models import Proveedor
from accounts_lilis.models import Usuario


def landing(request):
    return render(request, 'catalogo/landing.html')


def catalogo(request):
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/catalogo.html', {
        "categorias": categorias
    })


def subcatalogo(request, categoria):
    categoria_obj = get_object_or_404(Categoria, nombre=categoria)
    productos = Producto.objects.filter(categoria=categoria_obj)
    return render(request, "catalogo/subcatalogo.html", {
        "categoria": categoria_obj,
        "productos": productos
    })


def detalle_producto(request, producto):
    producto_obj = get_object_or_404(Producto, nombre=producto)
    categoria = producto_obj.categoria
    return render(request, "catalogo/detalle.html", {
        "producto": producto_obj.nombre,
        "detalle": producto_obj,
        "categoria": categoria.nombre
    })


def empresa(request):
    data = {
        "historia": "Dulcería Lilis nació en 1995...",
        "mision": "Endulzar la vida de nuestros clientes con productos artesanales.",
        "vision": "Ser reconocidos como la dulcería líder en innovación y calidad en la región.",
        "valores": ["Calidad", "Tradición", "Innovación", "Compromiso"],
        "contacto": "contacto@dulcerialilis.cl",
        "redes": {
            "Facebook": "https://facebook.com/dulcerialilis",
            "Instagram": "https://instagram.com/dulcerialilis"
        }
    }
    return render(request, "catalogo/empresa.html", data)


def tiene_permiso_productos(user):
    return user.is_authenticated and user.rol in ["ADMIN", "OPER_INVENTARIO", "OPER_PRODUCCION"]




@login_required
def mantenedores(request):
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_usuarios = Usuario.objects.count()

    return render(request, 'mantenedores/inicioMantenedores.html', {
        "total_productos": total_productos,
        "total_proveedores": total_proveedores,
        "total_usuarios": total_usuarios,
    })



@user_passes_test(tiene_permiso_productos)
@login_required
def MantenedorAgregarProducto(request):
    form = ProductoForm()
    return render(request, 'mantenedores/productos/MantenedorAgregarProducto.html', {'form': form})


@user_passes_test(tiene_permiso_productos)
@login_required
def mostrar_todos_productos(request):
    productos = Producto.objects.select_related("categoria").all()
    categorias = Categoria.objects.all()   
    return render(request, 'mantenedores/productos/todos_productos.html', {
        'productos': productos,
        'categorias': categorias
    })



@user_passes_test(tiene_permiso_productos)
@login_required
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto creado correctamente.")
            return redirect("mostrar_todos_productos")
        else:
            messages.error(request, "❌ Corrige los errores del formulario.")

    else:
        form = ProductoForm()

    return render(request, "mantenedores/productos/MantenedorAgregarProducto.html", {"form": form})



@user_passes_test(tiene_permiso_productos)
@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto modificado correctamente.")
            return redirect("mostrar_todos_productos")
        else:
            messages.error(request, "❌ Corrige los errores del formulario.")

    else:
        form = ProductoForm(instance=producto)

    return render(request, 'mantenedores/productos/MantenedorEditarProducto.html', {
        "form": form,
        "producto": producto
    })


@user_passes_test(lambda u: u.rol == "ADMIN")  
@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.delete()
        return redirect('mostrar_todos_productos')

    return render(request, 'mantenedores/confirmar_eliminacion.html', {'producto': producto})
