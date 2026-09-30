from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Proyecto, Tarea


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta registrada con este correo.')
        return email


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre del proyecto debe tener al menos 3 caracteres.')
        return nombre


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'proyecto', 'asignado_a', 'estado', 'prioridad', 'fecha_limite']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario is not None:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(propietario=usuario)

    def clean_fecha_limite(self):
        fecha_limite = self.cleaned_data.get('fecha_limite')
        if fecha_limite and fecha_limite < timezone.localdate():
            raise forms.ValidationError('La fecha límite no puede ser anterior a hoy.')
        return fecha_limite
