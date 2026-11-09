from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User

from .models import PrestacionMedica, EspecialidadMedica, PerfilUsuario
from .forms import PrestacionForm, RegistroUsuarioForm

def es_staff(user):
    return user.is_authenticated and user.is_staff

# --- MÓDULO 3: CATÁLOGO PÚBLICO Y READ ---
def catalogo_prestaciones(request):
    query = request.GET.get('q', '')
    especialidad_id = request.GET.get('especialidad', '')
    orden = request.GET.get('orden', 'nombre')

    prestaciones = PrestacionMedica.objects.select_related('especialidad').filter(is_active=True)

    if query:
        prestaciones = prestaciones.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        )

    if especialidad_id:
        prestaciones = prestaciones.filter(especialidad_id=especialidad_id)

    if orden in ['nombre', '-nombre', 'arancel', '-arancel']:
        prestaciones = prestaciones.order_by(orden)

    paginator = Paginator(prestaciones, 6) # 6 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    especialidades = EspecialidadMedica.objects.all()

    context = {
        'page_obj': page_obj,
        'especialidades': especialidades,
        'query': query,
        'especialidad_id': especialidad_id,
        'orden': orden,
    }
    return render(request, 'salud/catalogo.html', context)


def detalle_prestacion(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk)
    return render(request, 'salud/detalle.html', {'prestacion': prestacion})


# --- MÓDULO 3: CRUD PROTEGIDO (CREATE, UPDATE, DELETE) ---
@user_passes_test(es_staff)
def crear_prestacion(request):
    if request.method == 'POST':
        form = PrestacionForm(request.POST, request.FILES)
        if form.is_valid():
            prestacion = form.save()
            messages.success(request, f"La prestación '{prestacion.nombre}' fue creada con éxito.")
            return redirect('catalogo')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = PrestacionForm()
    return render(request, 'salud/formulario_prestacion.html', {'form': form, 'titulo': 'Nueva Prestación Médica'})


@user_passes_test(es_staff)
def editar_prestacion(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk)
    if request.method == 'POST':
        form = PrestacionForm(request.POST, request.FILES, instance=prestacion)
        if form.is_valid():
            form.save()
            messages.success(request, f"La prestación '{prestacion.nombre}' fue actualizada exitosamente.")
            return redirect('detalle_prestacion', pk=prestacion.pk)
        else:
            messages.error(request, "No se pudo guardar los cambios. Revisa los campos.")
    else:
        form = PrestacionForm(instance=prestacion)
    return render(request, 'salud/formulario_prestacion.html', {'form': form, 'titulo': f'Editar {prestacion.nombre}'})


@user_passes_test(es_staff)
def eliminar_prestacion(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk)
    if request.method == 'POST':
        # Baja lógica recomendada
        prestacion.is_active = False
        prestacion.save()
        messages.warning(request, f"La prestación '{prestacion.nombre}' ha sido desactivada (baja lógica).")
        return redirect('catalogo')
    return render(request, 'salud/confirmar_eliminar.html', {'prestacion': prestacion})


# --- MÓDULO 4: MANEJO DE SESIONES (CANASTA DE PRE-AGENDAMIENTO) ---
def agregar_canasta(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk, is_active=True)
    
    if prestacion.estado != 'DISPONIBLE':
        messages.error(request, "Esta prestación no se encuentra disponible actualmente para agendamiento.")
        return redirect('catalogo')

    canasta = request.session.get('canasta', {})
    pk_str = str(pk)

    if pk_str in canasta:
        canasta[pk_str]['cantidad'] += 1
    else:
        canasta[pk_str] = {
            'id': prestacion.id,
            'codigo': prestacion.codigo,
            'nombre': prestacion.nombre,
            'especialidad': prestacion.especialidad.nombre,
            'arancel': prestacion.arancel,
            'cantidad': 1
        }

    request.session['canasta'] = canasta
    messages.success(request, f"'{prestacion.nombre}' se agregó a tu canasta de pre-agendamiento.")
    return redirect('ver_canasta')


def actualizar_canasta(request, pk):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        canasta = request.session.get('canasta', {})
        pk_str = str(pk)

        if pk_str in canasta:
            if cantidad > 0:
                canasta[pk_str]['cantidad'] = cantidad
                messages.info(request, "Cantidad actualizada correctamente.")
            else:
                del canasta[pk_str]
                messages.warning(request, "Prestación eliminada de la canasta.")
            request.session['canasta'] = canasta

    return redirect('ver_canasta')


def eliminar_canasta(request, pk):
    canasta = request.session.get('canasta', {})
    pk_str = str(pk)
    if pk_str in canasta:
        del canasta[pk_str]
        request.session['canasta'] = canasta
        messages.warning(request, "Prestación quitada de la canasta.")
    return redirect('ver_canasta')


def vaciar_canasta(request):
    if 'canasta' in request.session:
        del request.session['canasta']
        messages.info(request, "Se ha vaciado la canasta de prestaciones.")
    return redirect('ver_canasta')


def ver_canasta(request):
    canasta = request.session.get('canasta', {})
    items = []
    subtotal = 0

    for item in canasta.values():
        total_item = item['arancel'] * item['cantidad']
        subtotal += total_item
        items.append({
            'id': item['id'],
            'codigo': item['codigo'],
            'nombre': item['nombre'],
            'especialidad': item['especialidad'],
            'arancel': item['arancel'],
            'cantidad': item['cantidad'],
            'total_item': total_item
        })

    # Desglose numérico/económico (Copago Estimado / Descuento Previsión Fonasa 20%)
    descuento_fonasa = int(subtotal * 0.20)
    total_final = subtotal - descuento_fonasa

    context = {
        'items': items,
        'subtotal': subtotal,
        'descuento_fonasa': descuento_fonasa,
        'total_final': total_final,
    }
    return render(request, 'salud/canasta.html', context)


@login_required
def confirmar_agendamiento(request):
    canasta = request.session.get('canasta', {})
    if not canasta:
        messages.error(request, "Tu canasta está vacía.")
        return redirect('catalogo')

    items = []
    subtotal = 0
    for item in canasta.values():
        total_item = item['arancel'] * item['cantidad']
        subtotal += total_item
        items.append(item)

    descuento_fonasa = int(subtotal * 0.20)
    total_final = subtotal - descuento_fonasa

    # Vaciar sesión tras simulación exitosa
    del request.session['canasta']

    context = {
        'items': items,
        'subtotal': subtotal,
        'descuento_fonasa': descuento_fonasa,
        'total_final': total_final,
        'usuario': request.user
    }
    return render(request, 'salud/resumen_agendamiento.html', context)


# --- AUTENTICACIÓN ---
def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            PerfilUsuario.objects.create(
                user=user,
                rut=data['rut'],
                telefono=data['telefono'],
                rol='PACIENTE'
            )
            login(request, user)
            messages.success(request, f"¡Bienvenido(a) {user.first_name}! Tu cuenta fue creada exitosamente.")
            return redirect('catalogo')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'salud/registro.html', {'form': form})


def login_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Hola de nuevo, {user.first_name or user.username}.")
            return redirect('catalogo')
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'salud/login.html', {'form': form})


def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('catalogo')
