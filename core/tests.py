from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ProyectoForm, TareaForm
from .models import Proyecto, Tarea


class ProyectoModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='clave12345')

    def test_creacion_proyecto(self):
        proyecto = Proyecto.objects.create(nombre='Web corporativa', propietario=self.usuario)
        self.assertEqual(str(proyecto), 'Web corporativa')
        self.assertEqual(proyecto.propietario, self.usuario)

    def test_un_usuario_puede_tener_varios_proyectos(self):
        Proyecto.objects.create(nombre='Proyecto A', propietario=self.usuario)
        Proyecto.objects.create(nombre='Proyecto B', propietario=self.usuario)
        self.assertEqual(self.usuario.proyectos.count(), 2)


class TareaModelTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='clave12345')
        self.proyecto = Proyecto.objects.create(nombre='App móvil', propietario=self.usuario)

    def test_creacion_tarea_con_valores_por_defecto(self):
        tarea = Tarea.objects.create(
            titulo='Diseñar wireframes',
            proyecto=self.proyecto,
            asignado_a=self.usuario,
        )
        self.assertEqual(tarea.estado, Tarea.Estado.PENDIENTE)
        self.assertEqual(tarea.prioridad, Tarea.Prioridad.MEDIA)
        self.assertEqual(str(tarea), 'Diseñar wireframes')

    def test_un_usuario_puede_gestionar_multiples_tareas(self):
        Tarea.objects.create(titulo='Tarea 1', proyecto=self.proyecto, asignado_a=self.usuario)
        Tarea.objects.create(titulo='Tarea 2', proyecto=self.proyecto, asignado_a=self.usuario)
        self.assertEqual(self.usuario.tareas.count(), 2)


class FormularioValidacionTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='clave12345')
        self.proyecto = Proyecto.objects.create(nombre='App móvil', propietario=self.usuario)

    def test_nombre_proyecto_demasiado_corto_es_invalido(self):
        form = ProyectoForm(data={'nombre': 'AB', 'descripcion': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_nombre_proyecto_valido(self):
        form = ProyectoForm(data={'nombre': 'Nuevo proyecto', 'descripcion': 'Detalle'})
        self.assertTrue(form.is_valid())

    def test_fecha_limite_pasada_es_invalida(self):
        ayer = timezone.localdate() - timedelta(days=1)
        form = TareaForm(
            data={
                'titulo': 'Tarea con fecha vencida',
                'descripcion': '',
                'proyecto': self.proyecto.pk,
                'asignado_a': self.usuario.pk,
                'estado': Tarea.Estado.PENDIENTE,
                'prioridad': Tarea.Prioridad.MEDIA,
                'fecha_limite': ayer,
            },
            usuario=self.usuario,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_limite', form.errors)


class AutenticacionYAccesoTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='clave12345')
        self.otro_usuario = User.objects.create_user(username='beto', password='clave12345')
        self.proyecto = Proyecto.objects.create(nombre='Proyecto privado', propietario=self.usuario)

    def test_dashboard_requiere_login(self):
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse('login'), respuesta.url)

    def test_dashboard_accesible_autenticado(self):
        self.client.login(username='ana', password='clave12345')
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)

    def test_usuario_no_puede_ver_proyecto_de_otro(self):
        self.client.login(username='beto', password='clave12345')
        respuesta = self.client.get(reverse('proyecto_detalle', args=[self.proyecto.pk]))
        self.assertEqual(respuesta.status_code, 404)

    def test_registro_crea_usuario_y_autentica(self):
        respuesta = self.client.post(reverse('registro'), {
            'username': 'carla',
            'email': 'carla@example.com',
            'password1': 'ClaveSegura123',
            'password2': 'ClaveSegura123',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(User.objects.filter(username='carla').exists())


class ProyectoTareaVistaTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='ana', password='clave12345')
        self.client.login(username='ana', password='clave12345')

    def test_crear_proyecto_asigna_propietario(self):
        respuesta = self.client.post(reverse('proyecto_crear'), {
            'nombre': 'Proyecto nuevo',
            'descripcion': 'Descripción de prueba',
        })
        self.assertEqual(respuesta.status_code, 302)
        proyecto = Proyecto.objects.get(nombre='Proyecto nuevo')
        self.assertEqual(proyecto.propietario, self.usuario)

    def test_crear_tarea_para_proyecto_propio(self):
        proyecto = Proyecto.objects.create(nombre='Proyecto X', propietario=self.usuario)
        respuesta = self.client.post(reverse('tarea_crear'), {
            'titulo': 'Nueva tarea',
            'descripcion': '',
            'proyecto': proyecto.pk,
            'asignado_a': self.usuario.pk,
            'estado': Tarea.Estado.PENDIENTE,
            'prioridad': Tarea.Prioridad.ALTA,
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Tarea.objects.filter(titulo='Nueva tarea', proyecto=proyecto).exists())

    def test_eliminar_proyecto(self):
        proyecto = Proyecto.objects.create(nombre='Proyecto a eliminar', propietario=self.usuario)
        respuesta = self.client.post(reverse('proyecto_eliminar', args=[proyecto.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(Proyecto.objects.filter(pk=proyecto.pk).exists())
