"""
Configuración de Django para pruebas unitarias.
Usa SQLite3 en lugar de PostgreSQL para testing.
"""

from .settings import *

# Usar SQLite3 para las pruebas
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de datos en memoria (más rápido)
    }
}

# Desabilitar migraciones para pruebas más rápidas (opcional)
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()  # Descomenta si quieres deshabilitar migraciones
