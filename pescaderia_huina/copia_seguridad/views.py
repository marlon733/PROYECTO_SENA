from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.serializers import serialize, deserialize
from django.apps import apps
import json
from datetime import datetime
import sys
from .models import CopiaSeguridadBD


def get_database_size():
    """Obtiene el tamaño estimado de la base de datos en bytes"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """)
            result = cursor.fetchone()
            return result[0] if result else "Desconocido"
    except:
        return "Desconocido (SQLite)"


def backup_all_data():
    """Crea un backup de todos los datos de la aplicación"""
    backup_data = {}
    
    # Apps a respaldar (excluir del sistema Django)
    apps_to_backup = [
        'usuarios', 'productos', 'proveedores', 'ventas', 'pedidos'
    ]
    
    try:
        for app_name in apps_to_backup:
            try:
                app_config = apps.get_app_config(app_name)
                # Serializar todos los modelos de la app
                for model in app_config.get_models():
                    model_name = model.__name__
                    queryset = model.objects.all()
                    
                    # Serializar con el formato JSON
                    serialized_data = serialize('json', queryset)
                    backup_data[f"{app_name}.{model_name}"] = json.loads(serialized_data)
            except Exception as e:
                backup_data[f"{app_name}_error"] = str(e)
    except Exception as e:
        backup_data["general_error"] = str(e)
    
    return backup_data


def restore_data(backup_data):
    """Restaura datos desde un backup"""
    errors = []
    restored_count = 0
    
    try:
        for model_path, objects_data in backup_data.items():
            if 'error' in model_path or not isinstance(objects_data, list):
                continue
            
            try:
                # Convertir de vuelta al formato JSON que Django espera deserializar
                json_str = json.dumps(objects_data)
                
                # Deserializar y guardar
                for obj in deserialize('json', json_str):
                    obj.save()
                    restored_count += 1
                    
            except Exception as e:
                errors.append(f"{model_path}: {str(e)}")
    except Exception as e:
        errors.append(f"Error general: {str(e)}")
    
    return restored_count, errors


@login_required
def lista_copias_seguridad(request):
    """Vista para listar las copias de seguridad"""
    copias = CopiaSeguridadBD.objects.all()
    context = {
        'copias': copias,
        'total_copias': copias.count(),
    }
    return render(request, 'copia_seguridad/lista_copias.html', context)


@login_required
@require_http_methods(["POST"])
def crear_copia_seguridad(request):
    """Crea una nueva copia de seguridad"""
    try:
        nombre = request.POST.get('nombre', f'Backup {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        descripcion = request.POST.get('descripcion', '')
        
        # Crear backup
        datos_backup = backup_all_data()
        tamaño = get_database_size()
        
        # Guardar en BD
        copia = CopiaSeguridadBD.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            datos_backup=datos_backup,
            tamaño_estimado=tamaño
        )
        
        messages.success(request, f'✓ Copia de seguridad "{nombre}" creada exitosamente')
        return redirect('copia_seguridad:lista')
        
    except Exception as e:
        messages.error(request, f'✗ Error al crear la copia: {str(e)}')
        return redirect('copia_seguridad:lista')


@login_required
@require_http_methods(["POST"])
def restaurar_copia_seguridad(request, copia_id):
    """Restaura una copia de seguridad"""
    try:
        copia = get_object_or_404(CopiaSeguridadBD, id=copia_id)
        
        # Restaurar datos
        restored_count, errors = restore_data(copia.datos_backup)
        
        # Actualizar fecha de restauración
        copia.fecha_restauracion = datetime.now()
        copia.save()
        
        if errors:
            messages.warning(
                request, 
                f'⚠ Restauración completada con información. '
                f'{restored_count} registros restaurados.'
            )
        else:
            messages.success(
                request, 
                f'✓ Copia "{copia.nombre}" restaurada exitosamente. '
                f'{restored_count} registros restaurados'
            )
        
        return redirect('copia_seguridad:lista')
        
    except Exception as e:
        messages.error(request, f'✗ Error al restaurar la copia: {str(e)}')
        return redirect('copia_seguridad:lista')


@login_required
@require_http_methods(["POST"])
def eliminar_copia_seguridad(request, copia_id):
    """Elimina una copia de seguridad"""
    try:
        copia = get_object_or_404(CopiaSeguridadBD, id=copia_id)
        nombre = copia.nombre
        copia.delete()
        messages.success(request, f'✓ Copia de seguridad "{nombre}" eliminada')
        return redirect('copia_seguridad:lista')
        
    except Exception as e:
        messages.error(request, f'✗ Error al eliminar la copia: {str(e)}')
        return redirect('copia_seguridad:lista')
