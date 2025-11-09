from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
import re
from .models import Usuario



def password_fuerte(value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r'\d', value):
        raise ValidationError("La contraseña debe contener al menos un número.")
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>/_\-]', value):
        raise ValidationError("La contraseña debe contener al menos un símbolo.")


def no_contiene_numeros(value):
    if re.search(r'\d', value):
        raise ValidationError("Este campo no puede contener números.")


def solo_letras(value):
    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$', value):
        raise ValidationError("Este campo solo puede contener letras.")



class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres, mayúscula, número y símbolo'
        }),
        min_length=8,
        validators=[password_fuerte]
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': 'Repite la contraseña'
        })
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.rol = "USUARIO"  
        if commit:
            user.save()
        return user



class UsuarioAdminForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'estado']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'ultimo_acceso': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'sesiones_activas': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()
        usuario_id = self.instance.id 

        if Usuario.objects.filter(username=username).exclude(id=usuario_id).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        usuario_id = self.instance.id  

        if Usuario.objects.filter(email=email).exclude(id=usuario_id).exists():
            raise ValidationError("Este correo ya está en uso.")

        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        if commit:
            usuario.save()  

        return usuario



class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not Usuario.objects.filter(email=email).exists():
            raise ValidationError("No existe una cuenta registrada con este correo.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        password_fuerte(password1)
        return password1