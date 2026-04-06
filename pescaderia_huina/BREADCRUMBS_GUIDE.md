# Guía de Implementación de Breadcrumbs

## 📍 Resumen

Se ha creado un sistema de **breadcrumbs (migas de pan)** para los módulos: pedidos, productos, ventas, proveedores e inventario.

### Archivos Creados (seguros, sin modificaciones innecesarias)
- ✅ `core/breadcrumbs.py` - Context processor que genera breadcrumbs automáticamente
- ✅ `core/templates/core/components/breadcrumb.html` - Componente template reutilizable

## 🚀 Implementación Paso a Paso

### PASO 1: Registrar el Context Processor

Edita `pescaderia_huina/settings.py` y agrega el context processor:

```python
TEMPLATES = [
    {
        # ... otras configuraciones ...
        'OPTIONS': {
            'context_processors': [
                # ... context processors existentes ...
                'core.breadcrumbs.get_breadcrumb_items',  # ← AGREGAR ESTA LÍNEA
            ],
        },
    },
]
```

### PASO 2: Actualizar panel_admin_base.html (MÍNIMA MODIFICACIÓN)

Solo reemplaza el bloque `{% block breadcrumb_items %}` en `core/templates/core/panel_admin_base.html` (línea ~875):

**Busca esto:**
```html
<nav aria-label="breadcrumb" class="mb-4">
    <ol class="breadcrumb small">
        {% block breadcrumb_items %}{% endblock %}
    </ol>
    <div class="d-flex justify-content-between align-items-end mt-2">
        {% block header_actions %}{% endblock %}
    </div>
</nav>
```

**Reemplaza por esto:**
```html
{% include "core/components/breadcrumb.html" %}
<div class="d-flex justify-content-between align-items-end mt-2">
    {% block header_actions %}{% endblock %}
</div>
```

### PASO 3: Verificar el Funcionamiento

Una vez actualizado settings.py y panel_admin_base.html, el breadcrumb funcionará automáticamente en:

#### ✅ Pedidos
- `/pedidos/` → Panel de control / Pedidos
- `/pedidos/nuevo/` → Panel de control / Pedidos / Nuevo Pedido
- `/pedidos/editar/<id>/` → Panel de control / Pedidos / Editar
- `/pedidos/detalle/<id>/` → Panel de control / Pedidos / Detalle
- `/pedidos/inventario/` → Panel de control / Pedidos / Inventario

#### ✅ Productos
- `/productos/` → Panel de control / Productos
- `/productos/nuevo/` → Panel de control / Productos / Nuevo Producto
- `/productos/<id>/editar/` → Panel de control / Productos / Editar
- `/productos/<id>/eliminar/` → Panel de control / Productos / Eliminar
- `/productos/<id>/` → Panel de control / Productos / Detalle

#### ✅ Ventas
- `/ventas/` → Panel de control / Ventas
- `/ventas/crear/` → Panel de control / Ventas / Nueva Venta
- `/ventas/<id>/editar/` → Panel de control / Ventas / Editar
- `/ventas/venta/<id>/` → Panel de control / Ventas / Detalle

#### ✅ Proveedores
- `/proveedores/` → Panel de control / Proveedores
- `/proveedores/nuevo/` → Panel de control / Proveedores / Nuevo
- `/proveedores/detalle/<id>/` → Panel de control / Proveedores / Detalle
- `/proveedores/modificar/<id>/` → Panel de control / Proveedores / Editar

## 🎨 Características del Breadcrumb

- ✨ Diseño moderno con gradientes y animaciones
- 🎯 Integración automática con las URLs
- 📱 Responsive en dispositivos móviles
- 🔗 Enlaces navegables (excepto el último item que muestra dónde está el usuario)
- 🏗️ Constructor genérico para rutas no mapeadas
- ⚙️ Fácil de personalizar los estilos

## 🔄 Personalización Avanzada

### Agregar Breadcrumbs Personalizados en una Vista

Si necesitas breadcrumbs diferentes en una plantilla específica, puedes sobrescribirlo:

```html
{% extends "core/panel_admin_base.html" %}

{% block breadcrumb_items %}
    <!-- Tu breadcrumb personalizado aquí -->
    <li class="breadcrumb-item">
        <a href="{% url 'pedidos:lista_pedidos' %}">Pedidos</a>
    </li>
    <li class="breadcrumb-item active">Mi Página Custom</li>
{% endblock %}
```

### Modificar Mapeos de URLs

Edita `core/breadcrumbs.py` en la sección `breadcrumb_map` para agregar más rutas o cambiar etiquetas.

## ⚠️ Notas de Seguridad

✅ **Sin modificaciones innecesarias:**
- Solo 2 archivos nuevo creados
- 1 línea agregada en settings.py
- 1 pequeño cambio en panel_admin_base.html

✅ **Sin riesgos:**
- El componente es independiente
- Todos los archivos originales permanecen íntegros
- Fácil de revertir si es necesario
- Fallback automático si algo falla

## 📋 Checklist de Implementación

- [ ] 1. Crear `core/breadcrumbs.py` ✅ (ya creado)
- [ ] 2. Crear `core/templates/core/components/breadcrumb.html` ✅ (ya creado)
- [ ] 3. Editar `pescaderia_huina/settings.py` (MANUAL - buscar TEMPLATES)
- [ ] 4. Editar `core/templates/core/panel_admin_base.html` (MANUAL - buscar breadcrumb nav)
- [ ] 5. Probar las navegaciones en cada módulo
- [ ] 6. Ajustar estilos si es necesario (en breadcrumb.html)

---

**Creado el:** 23 de marzo de 2026
**Autor:** Sistema de Breadcrumbs
**Versión:** 1.0
