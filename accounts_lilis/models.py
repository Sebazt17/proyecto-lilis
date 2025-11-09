from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .choices import ROLES_USUARIO, ESTADOS_USUARIO, AREAS_USUARIO


class Usuario(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Grupos',
        blank=True,
        related_name='usuarios_grupo',
        related_query_name='usuario',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Permisos de usuario',
        blank=True,
        related_name='usuarios_permiso',
        related_query_name='usuario',
    )

    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')

    telefono = models.CharField(max_length=20, verbose_name='Teléfono', blank=True, null=True)

    rol = models.CharField(max_length=20, choices=ROLES_USUARIO, default='USUARIO', verbose_name='Rol')
    estado = models.CharField(max_length=10, choices=ESTADOS_USUARIO, default='ACTIVO', verbose_name='Estado')
    mfa_habilitado = models.BooleanField(default=False, verbose_name='MFA Habilitado')
    ultimo_acceso = models.DateTimeField(null=True, blank=True, verbose_name='Último Acceso')
    sesiones_activas = models.PositiveIntegerField(default=0, verbose_name='Sesiones Activas')

    area = models.CharField(max_length=30, choices=AREAS_USUARIO, blank=True, null=True, verbose_name='Área/Unidad')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    requiere_cambio_password = models.BooleanField(default=False, verbose_name="Requiere cambio de contraseña")

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
