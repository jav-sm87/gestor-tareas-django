from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ProyectoForm, RegistroForm, TareaForm
from .models import Proyecto, Tarea


class RegistroView(View):
    template_name = 'registration/registro.html'

    def get(self, request):
        form = RegistroForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido, {usuario.username}! Tu cuenta fue creada correctamente.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyectos = Proyecto.objects.filter(propietario=self.request.user)
        tareas = Tarea.objects.filter(proyecto__propietario=self.request.user)
        context['total_proyectos'] = proyectos.count()
        context['total_tareas'] = tareas.count()
        context['tareas_pendientes'] = tareas.filter(estado=Tarea.Estado.PENDIENTE).count()
        context['tareas_completadas'] = tareas.filter(estado=Tarea.Estado.COMPLETADA).count()
        context['proyectos_recientes'] = proyectos[:5]
        context['tareas_recientes'] = tareas[:5]
        return context


class ProyectoQuerysetMixin:
    """Restringe el acceso a los proyectos que pertenecen al usuario autenticado."""

    def get_queryset(self):
        return Proyecto.objects.filter(propietario=self.request.user)


class ProyectoListView(LoginRequiredMixin, ProyectoQuerysetMixin, ListView):
    model = Proyecto
    template_name = 'core/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 10


class ProyectoDetailView(LoginRequiredMixin, ProyectoQuerysetMixin, DetailView):
    model = Proyecto
    template_name = 'core/proyecto_detail.html'
    context_object_name = 'proyecto'


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'core/proyecto_form.html'

    def form_valid(self, form):
        form.instance.propietario = self.request.user
        messages.success(self.request, 'Proyecto creado correctamente.')
        return super().form_valid(form)


class ProyectoUpdateView(LoginRequiredMixin, ProyectoQuerysetMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'core/proyecto_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto actualizado correctamente.')
        return super().form_valid(form)


class ProyectoDeleteView(LoginRequiredMixin, ProyectoQuerysetMixin, DeleteView):
    model = Proyecto
    template_name = 'core/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto eliminado correctamente.')
        return super().form_valid(form)


class TareaQuerysetMixin:
    """Restringe el acceso a las tareas de los proyectos del usuario autenticado."""

    def get_queryset(self):
        return Tarea.objects.filter(proyecto__propietario=self.request.user)


class TareaListView(LoginRequiredMixin, TareaQuerysetMixin, ListView):
    model = Tarea
    template_name = 'core/tarea_list.html'
    context_object_name = 'tareas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.GET.get('estado')
        busqueda = self.request.GET.get('q')
        if estado:
            queryset = queryset.filter(estado=estado)
        if busqueda:
            queryset = queryset.filter(
                Q(titulo__icontains=busqueda) | Q(descripcion__icontains=busqueda)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Tarea.Estado.choices
        context['estado_actual'] = self.request.GET.get('estado', '')
        context['busqueda_actual'] = self.request.GET.get('q', '')
        return context


class TareaDetailView(LoginRequiredMixin, TareaQuerysetMixin, DetailView):
    model = Tarea
    template_name = 'core/tarea_detail.html'
    context_object_name = 'tarea'


class TareaCreateView(LoginRequiredMixin, CreateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'core/tarea_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Tarea creada correctamente.')
        return super().form_valid(form)


class TareaUpdateView(LoginRequiredMixin, TareaQuerysetMixin, UpdateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'core/tarea_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Tarea actualizada correctamente.')
        return super().form_valid(form)


class TareaDeleteView(LoginRequiredMixin, TareaQuerysetMixin, DeleteView):
    model = Tarea
    template_name = 'core/tarea_confirm_delete.html'
    success_url = reverse_lazy('tarea_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Tarea eliminada correctamente.')
        return super().form_valid(form)
