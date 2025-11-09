from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

from .views import (
    RegisterView,
    login_personalizado,
    check_email,
    usuario_listar,
    usuario_agregar,
    usuario_editar,
    usuario_eliminar,
    CambioPasswordObligatorioView  
)

app_name = "accounts_lilis"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_personalizado, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path(
        "cambiar-password-obligatorio/",
        CambioPasswordObligatorioView.as_view(),
        name="cambiar_password_obligatorio"
    ),

    path("usuarios/", usuario_listar, name="usuario_listar"),
    path("usuarios/agregar/", usuario_agregar, name="usuario_agregar"),
    path("usuarios/editar/<int:id>/", usuario_editar, name="usuario_editar"),
    path("usuarios/eliminar/<int:id>/", usuario_eliminar, name="usuario_eliminar"),
    path("check_email/", check_email, name="check_email"),

    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts_lilis/password_reset_form.html",
            html_email_template_name="accounts_lilis/password_reset_email.html",
            email_template_name="accounts_lilis/password_reset_email.txt",
            subject_template_name="accounts_lilis/password_reset_subject.txt",
            form_class=CustomPasswordResetForm,
            success_url="/accounts/password_reset/done/"
        ),
        name="password_reset",
    ),

    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts_lilis/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts_lilis/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url="/accounts/reset/done/"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts_lilis/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
