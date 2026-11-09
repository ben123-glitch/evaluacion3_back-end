from django.urls import path
from . import views

urlpatterns = [
    # Catálogo y detalle
    path('', views.catalogo_prestaciones, name='catalogo'),
    path('prestacion/<int:pk>/', views.detalle_prestacion, name='detalle_prestacion'),
    
    # CRUD Operativo Protegido
    path('prestacion/nueva/', views.crear_prestacion, name='crear_prestacion'),
    path('prestacion/<int:pk>/editar/', views.editar_prestacion, name='editar_prestacion'),
    path('prestacion/<int:pk>/eliminar/', views.eliminar_prestacion, name='eliminar_prestacion'),
    
    # Canasta en Sesión
    path('canasta/', views.ver_canasta, name='ver_canasta'),
    path('canasta/agregar/<int:pk>/', views.agregar_canasta, name='agregar_canasta'),
    path('canasta/actualizar/<int:pk>/', views.actualizar_canasta, name='actualizar_canasta'),
    path('canasta/eliminar/<int:pk>/', views.eliminar_canasta, name='eliminar_canasta'),
    path('canasta/vaciar/', views.vaciar_canasta, name='vaciar_canasta'),
    path('canasta/confirmar/', views.confirmar_agendamiento, name='confirmar_agendamiento'),
    
    # Auth
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
]
