from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from salud.models import EspecialidadMedica, PrestacionMedica, PerfilUsuario

class Command(BaseCommand):
    help = 'Pobla la base de datos con especialidades, prestaciones y usuarios de prueba.'

    def handle(self, *args, **options):
        self.stdout.write("Poblando base de datos del Centro Médico Vitalis...")

        # 1. Crear Especialidades Médicas (4 clasificadores)
        esp_cardio, _ = EspecialidadMedica.objects.get_or_create(
            nombre="Cardiología", 
            defaults={"descripcion": "Diagnóstico y tratamiento de afecciones del corazón y vasos sanguíneos.", "icono": "fa-heartbeat"}
        )
        esp_derma, _ = EspecialidadMedica.objects.get_or_create(
            nombre="Dermatología", 
            defaults={"descripcion": "Cuidado integral de la piel, cabello y uñas.", "icono": "fa-allergies"}
        )
        esp_ped, _ = EspecialidadMedica.objects.get_or_create(
            nombre="Pediatría", 
            defaults={"descripcion": "Atención médica especializada para bebés, niños y adolescentes.", "icono": "fa-baby"}
        )
        esp_trauma, _ = EspecialidadMedica.objects.get_or_create(
            nombre="Traumatología", 
            defaults={"descripcion": "Evaluación y tratamiento del sistema musculoesquelético.", "icono": "fa-bone"}
        )

        # 2. Crear Prestaciones Médicas (8 entidades principales)
        prestaciones = [
            {"codigo": "CAR-001", "nombre": "Electrocardiograma de Reposo (EKG)", "especialidad": esp_cardio, "arancel": 25000, "duracion_minutos": 20, "descripcion": "Examen que registra la actividad eléctrica del corazón. Requiere reposo previo de 10 min."},
            {"codigo": "CAR-002", "nombre": "Ecocardiograma Doppler", "especialidad": esp_cardio, "arancel": 68000, "duracion_minutos": 45, "descripcion": "Ultrasonido del corazón para evaluar válvulas y función cardíaca."},
            {"codigo": "DER-001", "nombre": "Dermatoscopía de Lunares", "especialidad": esp_derma, "arancel": 35000, "duracion_minutos": 30, "descripcion": "Evaluación microscópica de lesiones pigmentadas en la piel."},
            {"codigo": "DER-002", "nombre": "Crioterapia de Lesiones Cutáneas", "especialidad": esp_derma, "arancel": 42000, "duracion_minutos": 25, "descripcion": "Tratamiento mediante nitrógeno líquido para verrugas o queratosis."},
            {"codigo": "PED-001", "nombre": "Control de Niño Sano", "especialidad": esp_ped, "arancel": 30000, "duracion_minutos": 30, "descripcion": "Evaluación del desarrollo psicomotor, peso, talla y esquema de vacunación."},
            {"codigo": "PED-002", "nombre": "Evaluación del Desarrollo Infantil", "especialidad": esp_ped, "arancel": 38000, "duracion_minutos": 40, "descripcion": "Chequeo pediátrico integral para etapa preescolar."},
            {"codigo": "TRA-001", "nombre": "Radiografía de Rodilla (Par)", "especialidad": esp_trauma, "arancel": 28000, "duracion_minutos": 15, "descripcion": "Estudio radiológico simple en proyección AP y Lateral."},
            {"codigo": "TRA-002", "nombre": "Infiltración Articular Guiada", "especialidad": esp_trauma, "arancel": 55000, "duracion_minutos": 30, "descripcion": "Procedimiento de alivio del dolor articular con corticoides o viscosuplementación."}
        ]

        for p in prestaciones:
            PrestacionMedica.objects.get_or_create(
                codigo=p["codigo"],
                defaults={
                    "nombre": p["nombre"],
                    "especialidad": p["especialidad"],
                    "arancel": p["arancel"],
                    "duracion_minutos": p["duracion_minutos"],
                    "descripcion": p["descripcion"],
                    "estado": 'DISPONIBLE',
                    "is_active": True
                }
            )

        # 3. Crear Usuarios de Prueba (Admin y Paciente)
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser("admin", "admin@vitalis.cl", "admin123")
            admin_user.first_name = "Administrador"
            admin_user.last_name = "Vitalis"
            admin_user.save()
            PerfilUsuario.objects.create(user=admin_user, rut="11.111.111-1", telefono="+56911112222", rol="PERSONAL")
            self.stdout.write("Usuario admin creado (admin / admin123)")

        if not User.objects.filter(username="paciente").exists():
            paciente_user = User.objects.create_user("paciente", "paciente@vitalis.cl", "paciente123")
            paciente_user.first_name = "Juan"
            paciente_user.last_name = "Pérez"
            paciente_user.save()
            PerfilUsuario.objects.create(user=paciente_user, rut="22.222.222-2", telefono="+56933334444", rol="PACIENTE")
            self.stdout.write("Usuario paciente creado (paciente / paciente123)")

        self.stdout.write(self.style.SUCCESS("¡Base de datos poblada exitosamente!"))
