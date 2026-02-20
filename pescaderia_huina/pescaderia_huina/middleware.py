import os
from django.conf import settings
from django.http import FileResponse
from django.utils.deprecation import MiddlewareMixin


class ServeStaticFilesMiddleware(MiddlewareMixin):
    """
    Middleware para servir archivos estáticos en desarrollo con DEBUG = False
    """
    
    def process_request(self, request):
        # Si la ruta comienza con /static/
        if request.path.startswith(settings.STATIC_URL):
            # Quitar el prefijo /static/
            file_path = request.path[len(settings.STATIC_URL):]
            
            # Construir la ruta completa del archivo
            full_path = os.path.join(settings.STATIC_ROOT, file_path)
            
            # Validar que el archivo existe y está dentro de STATIC_ROOT
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Servir el archivo
                return FileResponse(
                    open(full_path, 'rb'),
                    content_type=self.get_content_type(full_path)
                )
        
        return None
    
    @staticmethod
    def get_content_type(file_path):
        """
        Retorna el content-type basado en la extensión del archivo
        """
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.mp4': 'video/mp4',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.webp': 'image/webp',
        }
        return content_types.get(ext, 'application/octet-stream')
