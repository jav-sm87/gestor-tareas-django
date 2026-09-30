from django.conf import settings
from django.db import models
from django.urls import reverse


class Proyecto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proyectos',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('proyecto_detalle', kwargs={'pk': self.pk})


class Tarea(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PEN', 'Pendiente'
        EN_PROGRESO = 'PRO', 'En progreso'
        COMPLETADA = 'COM', 'Completada'

    class Prioridad(models.TextChoices):
        BAJA = 'BAJ', 'Baja'
        MEDIA = 'MED', 'Media'
        ALTA = 'ALT', 'Alta'

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tareas',
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas',
    )
    estado = models.CharField(max_length=3, choices=Estado.choices, default=Estado.PENDIENTE)
    prioridad = models.CharField(max_length=3, choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_limite', '-prioridad']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('tarea_detalle', kwargs={'pk': self.pk})
