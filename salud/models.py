from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class EspecialidadMedica(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Especialidad")
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    icono = models.CharField(max_length=50, default="fa-stethoscope", verbose_name="Ícono FontAwesome")

    class Meta:
        verbose_name = "Especialidad Médica"
        verbose_name_plural = "Especialidades Médicas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PrestacionMedica(models.Model):
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('SUSPENDIDO', 'Suspendido'),
        ('SIN_CUPOS', 'Sin Cupos'),
    ]

    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código de Prestación")
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Prestación / Examen")
    especialidad = models.ForeignKey(
        EspecialidadMedica, 
        on_delete=models.PROTECT, 
        related_name="prestaciones",
        verbose_name="Especialidad Médica"
    )
    descripcion = models.TextField(verbose_name="Descripción y Requisitos")
    arancel = models.IntegerField(
        validators=[MinValueValidator(0)], 
        verbose_name="Arancel / Precio (CLP)"
    )
    duracion_minutos = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5)],
        verbose_name="Duración Estimada (Minutos)"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='DISPONIBLE',
        verbose_name="Estado Operativo"
    )
    imagen = models.ImageField(
        upload_to='prestaciones/', 
        blank=True, 
        null=True,
        verbose_name="Imagen Representativa"
    )
    is_active = models.BooleanField(default=True, verbose_name="Vigente (Baja Lógica)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Prestación Médica"
        verbose_name_plural = "Prestaciones Médicas"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.especialidad.nombre})"


class PerfilUsuario(models.Model):
    ROLES = [
        ('PACIENTE', 'Paciente'),
        ('PERSONAL', 'Personal Administrativo / Médico'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, verbose_name="RUT")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de Contacto")
    rol = models.CharField(max_length=20, choices=ROLES, default='PACIENTE', verbose_name="Rol Institucional")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.rut})"
