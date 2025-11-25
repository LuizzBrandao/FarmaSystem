"""
Middleware para garantir encoding UTF-8 em todas as respostas HTTP
"""
from django.utils.deprecation import MiddlewareMixin


class UTF8ResponseMiddleware(MiddlewareMixin):
    """
    Middleware que força charset UTF-8 em todas as respostas HTTP
    para garantir que caracteres especiais sejam exibidos corretamente
    """
    
    def process_response(self, request, response):
        # Garantir que o Content-Type inclua charset=utf-8
        content_type = response.get('Content-Type', '')
        
        # Se não tem charset especificado e é conteúdo de texto
        if 'charset' not in content_type.lower():
            if content_type.startswith('text/'):
                # Adicionar charset=utf-8 ao Content-Type existente
                if content_type:
                    response['Content-Type'] = f"{content_type}; charset=utf-8"
                else:
                    response['Content-Type'] = 'text/html; charset=utf-8'
            elif not content_type or content_type.startswith('text/html'):
                # Para HTML, sempre garantir UTF-8
                response['Content-Type'] = 'text/html; charset=utf-8'
        
        return response

