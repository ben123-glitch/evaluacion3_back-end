from django.contrib import admin
from .models import EspecialidadMedica, PrestacionMedica, PerfilUsuario

# 1. Personalización Corporativa del Administrador (Criterio 2.1.2)
admin.site.site_header = 'Centro Médico Vitalis - Panel de Control'
admin.site.site_title = 'Centro Médico Vitalis Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'

@admin.register(EspecialidadMedica)
class EspecialidadMedicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(PrestacionMedica)
class PrestacionMedicaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'especialidad', 'arancel', 'duracion_minutos', 'estado', 'is_active')
    list_filter = ('especialidad', 'estado', 'is_active')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('arancel', 'estado', 'is_active')
    
    fieldsets = (
        ('Identificación del Recurso', {
            'fields': ('codigo', 'nombre', 'especialidad', 'imagen')
        }),
        ('Detalles Operativos y Tarifas', {
            'fields': ('descripcion', 'arancel', 'duracion_minutos', 'estado', 'is_active')
        }),
    )

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'rol')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut')
    list_filter = ('rol',)
