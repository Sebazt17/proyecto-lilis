from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from .models import Usuario
from .forms import RegisterForm, UsuarioAdminForm, CustomSetPasswordForm

import random
import string
from django.core.mail import send_mail



class RegisterView(View):
    template_name = "accounts_lilis/register.html"

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "✅ Registro exitoso. ¡Bienvenido/a!")
            auth_login(request, user)
            return redirect("landing")

        messages.error(request, "❌ Revisa los errores del formulario.")
        return render(request, self.template_name, {"form": form})



def permiso_admin(user):
    return user.is_authenticated and user.rol == "ADMIN"



@login_required
@user_passes_test(permiso_admin)
def usuario_listar(request):
    usuarios = Usuario.objects.all().order_by("id")
    return render(request, "mantenedores/usuarios/usuarios_listar.html", {"usuarios": usuarios})


@login_required
@user_passes_test(permiso_admin)
def usuario_agregar(request):
    form = UsuarioAdminForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            usuario = form.save(commit=False)

            temp_pass = "LILIS-" + ''.join(random.choices(string.ascii_letters + string.digits, k=6)) + "!"
            usuario.set_password(temp_pass)
            usuario.requiere_cambio_password = True  
            usuario.save()

            send_mail(
                subject="Bienvenido/a a Dulcería Lilis",
                message=f"""
                        Hola {usuario.first_name},

                        Tu cuenta ha sido creada en Dulcería Lilis.

                        Usuario: {usuario.username}
                        Contraseña temporal: {temp_pass}

                        Al iniciar sesión deberás cambiar tu contraseña.

                        Saludos,
                        Dulcería Lilis
                """,
                from_email="sopporte.apparduino@gmail.com",
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            messages.success(request, "✅ Usuario creado y contraseña temporal enviada por correo.")
            return redirect("accounts_lilis:usuario_listar")

        messages.error(request, "❌ Revisa los errores del formulario.")

    return render(request, "mantenedores/usuarios/usuarios_agregar.html", {"form": form})


@login_required
@user_passes_test(permiso_admin)
def usuario_editar(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    form = UsuarioAdminForm(request.POST or None, instance=usuario)

    form.fields.pop("password1", None)
    form.fields.pop("password2", None)

    if usuario.username == "admin_principal":
        form.fields["rol"].disabled = True
        form.fields["estado"].disabled = True

    if request.method == "POST":
        if form.is_valid():

            usuario = form.save(commit=False)

            if usuario.username == "admin_principal":
                usuario.rol = "ADMIN"
                usuario.estado = "ACTIVO"

            usuario.save()    

            messages.success(request, "✅ Usuario modificado correctamente.")
            return redirect("accounts_lilis:usuario_listar")
        else:
            print("ERRORES:", form.errors)   

    return render(
        request,
        "mantenedores/usuarios/usuarios_editar.html",
        {"form": form, "usuario": usuario}
    )




@login_required
@user_passes_test(permiso_admin)
def usuario_eliminar(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if usuario.username == "admin_principal":
        messages.error(request, "🚫 No puedes eliminar al administrador principal.")
        return redirect("accounts_lilis:usuario_listar")

    usuario.delete()
    messages.success(request, "✅ Usuario eliminado.")
    return redirect("accounts_lilis:usuario_listar")




def login_personalizado(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            if user.estado == "BLOQUEADO":
                messages.error(request, "🚫 Tu cuenta está bloqueada. Contacta al administrador.")
                return redirect("accounts_lilis:login")

            if not user.is_active:
                messages.error(request, "🚫 Usuario desactivado. Contacta al administrador.")
                return redirect("accounts_lilis:login")

            auth_login(request, user)

            if user.requiere_cambio_password:
                return redirect("accounts_lilis:cambiar_password_obligatorio")

            if user.rol == "ADMIN":
                return redirect("mantenedores")

            return redirect("landing")

        messages.error(request, "❌ Usuario o contraseña incorrectos")

    return render(request, "accounts_lilis/login.html")





class CambioPasswordObligatorioView(PasswordChangeView):
    template_name = "accounts_lilis/password_reset_temporal.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("accounts_lilis:password_reset_complete")

    def form_valid(self, form):
        usuario = self.request.user
        usuario.requiere_cambio_password = False  
        usuario.save()
        messages.success(self.request, "✅ Contraseña actualizada correctamente.")
        return super().form_valid(form)



def check_email(request):
    email = request.GET.get("email")
    exists = Usuario.objects.filter(email=email).exists()
    return JsonResponse({"exists": exists})
