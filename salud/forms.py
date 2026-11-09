from django import forms
from django.contrib.auth.models import User
from .models import PrestacionMedica, PerfilUsuario

class PrestacionForm(forms.ModelForm):
    class Meta:
        model = PrestacionMedica
        fields = ['codigo', 'nombre', 'especialidad', 'descripcion', 'arancel', 'duracion_minutos', 'estado', 'imagen', 'is_active']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CAR-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Electrocardiograma de reposo'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Indicaciones previas y requisitos...'}),
            'arancel': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_arancel(self):
        arancel = self.cleaned_data.get('arancel')
        if arancel is not None and arancel < 0:
            raise forms.ValidationError("El arancel no puede ser un número negativo.")
        return arancel

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if PrestacionMedica.objects.filter(codigo__iexact=codigo).exclude(pk=instance.pk).exists():
                raise forms.ValidationError("Este código de prestación ya existe en el sistema.")
        else:
            if PrestacionMedica.objects.filter(codigo__iexact=codigo).exists():
                raise forms.ValidationError("Este código de prestación ya existe en el sistema.")
        return codigo.upper()


class RegistroUsuarioForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    rut = forms.CharField(max_length=12, label="RUT", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}))
    telefono = forms.CharField(max_length=15, label="Teléfono", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Contraseña")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está registrado.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data
