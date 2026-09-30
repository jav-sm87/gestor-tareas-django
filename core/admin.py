from django.contrib import admin

from .models import Proyecto, Tarea


class TareaInline(admin.TabularInline):
    model = Tarea
    extra = 0
    fields = ['titulo', 'asignado_a', 'estado', 'prioridad', 'fecha_limite']


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'propietario', 'fecha_creacion', 'total_tareas']
    list_filter = ['fecha_creacion', 'propietario']
    search_fields = ['nombre', 'descripcion', 'propietario__username']
    date_hierarchy = 'fecha_creacion'
    inlines = [TareaInline]

    @admin.display(description='N.º de tareas')
    def total_tareas(self, obj):
        return obj.tareas.count()


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'asignado_a', 'estado', 'prioridad', 'fecha_limite']
    list_filter = ['estado', 'prioridad', 'proyecto']
    search_fields = ['titulo', 'descripcion', 'asignado_a__username']
    list_editable = ['estado', 'prioridad']
    autocomplete_fields = ['proyecto', 'asignado_a']
    date_hierarchy = 'fecha_limite'
