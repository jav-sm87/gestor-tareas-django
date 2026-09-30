# Gestor de Tareas y Proyectos

Aplicación web desarrollada con Django que permite a los usuarios registrarse,
autenticarse y gestionar sus propios proyectos y tareas.

## Características

- Registro y autenticación de usuarios (`django.contrib.auth`).
- Redirecciones configuradas tras iniciar/cerrar sesión.
- Acceso restringido a las vistas mediante `LoginRequiredMixin`.
- CRUD completo de **Proyectos** y **Tareas**, con relación uno-a-muchos entre
  un usuario y sus proyectos, y entre un proyecto y sus tareas.
- Cada usuario solo puede ver, editar y eliminar sus propios proyectos y tareas
  (aislamiento de datos entre usuarios).
- Formularios con validaciones personalizadas (`forms.ModelForm`):
  nombre de proyecto con largo mínimo, fecha límite de tarea no puede ser
  pasada, correo de registro único.
- Plantillas con herencia (`base.html`) y contenido dinámico vía contexto.
- Panel (`dashboard`) con estadísticas de proyectos y tareas.
- Filtro y búsqueda de tareas por estado y texto.
- Sitio administrativo personalizado (`admin.py`) con listados, filtros,
  búsqueda y tareas inline dentro de cada proyecto.
- Protección CSRF en todos los formularios (`{% csrf_token %}`).
- Pruebas unitarias para modelos, formularios y vistas (`core/tests.py`).

## Estructura del proyecto

```
MODULO 6/
├── manage.py
├── requirements.txt
├── gestor_tareas/          # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
└── core/                   # App principal
    ├── models.py           # Modelos Proyecto y Tarea
    ├── forms.py            # RegistroForm, ProyectoForm, TareaForm
    ├── views.py            # Vistas basadas en clases (CRUD + dashboard)
    ├── urls.py             # Rutas de la app
    ├── admin.py            # Configuración del sitio administrativo
    ├── tests.py            # Pruebas unitarias
    └── templates/
        ├── core/           # base.html, dashboard, proyecto_*, tarea_*
        └── registration/   # login.html, registro.html
```

## Modelos

- **Proyecto**: `nombre`, `descripcion`, `propietario` (FK a `User`), `fecha_creacion`.
- **Tarea**: `titulo`, `descripcion`, `proyecto` (FK a `Proyecto`),
  `asignado_a` (FK a `User`), `estado` (Pendiente/En progreso/Completada),
  `prioridad` (Baja/Media/Alta), `fecha_limite`, `fecha_creacion`.

Un usuario puede tener múltiples proyectos, y cada proyecto puede tener
múltiples tareas asignadas a distintos usuarios.

## Instalación

1. **Requisitos previos**: Python 3.10+ instalado.

2. Clonar o descargar el proyecto y ubicarse en la carpeta raíz (donde está
   `manage.py`).

3. Crear y activar un entorno virtual (recomendado):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

4. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Aplicar las migraciones de la base de datos:

   ```bash
   python manage.py migrate
   ```

6. Crear un superusuario para acceder al sitio administrativo:

   ```bash
   python manage.py createsuperuser
   ```

7. Ejecutar el servidor de desarrollo:

   ```bash
   python manage.py runserver
   ```

8. Abrir el navegador en `http://127.0.0.1:8000/`.

## Uso

- **Registro**: `http://127.0.0.1:8000/registro/` crea una cuenta nueva y
  autentica automáticamente al usuario.
- **Inicio de sesión**: `http://127.0.0.1:8000/accounts/login/`.
- **Panel principal**: `http://127.0.0.1:8000/` muestra un resumen de
  proyectos y tareas del usuario autenticado.
- **Proyectos**: `http://127.0.0.1:8000/proyectos/` — crear, ver, editar y
  eliminar proyectos propios.
- **Tareas**: `http://127.0.0.1:8000/tareas/` — crear, ver, editar y eliminar
  tareas, con filtro por estado y búsqueda por texto.
- **Administración**: `http://127.0.0.1:8000/admin/` — gestión avanzada de
  usuarios, proyectos y tareas (requiere superusuario).

## Ejecutar las pruebas

```bash
python manage.py test core
```

Las pruebas cubren:

- Creación de modelos y relación usuario-proyectos-tareas.
- Validaciones personalizadas de formularios (nombre de proyecto, fecha
  límite).
- Restricción de acceso a usuarios no autenticados (`LoginRequiredMixin`).
- Aislamiento de datos: un usuario no puede acceder a proyectos de otro
  (respuesta 404).
- Flujo de registro, creación, edición y eliminación de proyectos/tareas.
