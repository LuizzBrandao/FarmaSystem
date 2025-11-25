"""
Módulo robusto para geração de PDFs com fallbacks e otimizações
Suporta WeasyPrint (preferido) e ReportLab (fallback)
"""

import io
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from django.http import HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Count, Q, Min, Max
from django.core.paginator import Paginator

# Tentativa de importação das bibliotecas PDF
PDF_ENGINE = None
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    PDF_ENGINE = 'weasyprint'
    print("[OK] WeasyPrint disponivel - usando como engine principal")
except (ImportError, OSError, Exception) as e:
    # Captura ImportError, OSError (bibliotecas GTK+ não encontradas no Windows)
    # e qualquer outra exceção durante a importação do WeasyPrint
    try:
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        PDF_ENGINE = 'reportlab'
        error_msg = str(e)[:100] if e else "erro desconhecido"
        print(f"[AVISO] WeasyPrint nao disponivel ({type(e).__name__}: {error_msg}) - usando ReportLab como fallback")
    except ImportError:
        PDF_ENGINE = None
        print("[ERRO] Nenhuma biblioteca PDF disponivel - instale WeasyPrint ou ReportLab")

# Logger específico para PDFs
logger = logging.getLogger('apps.reports.pdf')

class PDFGenerationError(Exception):
    """Exceção customizada para erros de geração de PDF"""
    pass

class PDFGenerator:
    """
    Classe robusta para geração de PDFs com múltiplas engines e fallbacks
    """
    
    def __init__(self):
        """Inicializar gerador com configurações otimizadas"""
        self.font_config = None
        self.timeout = getattr(settings, 'PDF_GENERATION_TIMEOUT', 60)
        self.max_pages = getattr(settings, 'PDF_MAX_PAGES', 500)
        self.chunk_size = getattr(settings, 'PDF_CHUNK_SIZE', 1000)
        
        if PDF_ENGINE == 'weasyprint':
            try:
                from weasyprint.text.fonts import FontConfiguration
                self.font_config = FontConfiguration()
            except (ImportError, OSError, Exception):
                # Se FontConfiguration falhar, continuar sem ele
                self.font_config = None
        
        logger.info(f"PDFGenerator inicializado com engine: {PDF_ENGINE}")
    
    def generate_stock_report_pdf(self, request: HttpRequest) -> HttpResponse:
        """
        Gerar relatório de estoque em PDF
        """
        logger.info("Iniciando geração do relatório de estoque")
        
        try:
            # Verificar disponibilidade da engine
            if not PDF_ENGINE:
                raise PDFGenerationError("Nenhuma biblioteca PDF disponível")
            
            # 1. Buscar dados otimizados
            medicamentos_data = self._get_stock_data_optimized()
            
            # 2. Calcular métricas
            metrics = self._calculate_stock_metrics(medicamentos_data)
            
            # 3. Preparar contexto
            context = {
                'medicamentos': medicamentos_data,
                'metrics': metrics,
                'generated_at': timezone.now(),
                'user': request.user,
                'title': 'Relatório de Estoque',
                'company_name': 'Sistema de Farmácia',
                'report_type': 'stock',
            }
            
            # 4. Gerar PDF baseado na engine disponível
            if PDF_ENGINE == 'weasyprint':
                return self._generate_with_weasyprint(request, context, 'reports/pdf/stock_report.html')
            else:
                return self._generate_with_reportlab_stock(context)
                
        except Exception as e:
            logger.error(f"Erro na geração do PDF de estoque: {str(e)}", exc_info=True)
            return self._generate_error_pdf("Relatório de Estoque", str(e))
    
    def generate_movements_report_pdf(self, request: HttpRequest) -> HttpResponse:
        """
        Gerar relatório de movimentações em PDF (últimos 30 dias)
        """
        logger.info("Iniciando geração do relatório de movimentações")
        
        try:
            if not PDF_ENGINE:
                raise PDFGenerationError("Nenhuma biblioteca PDF disponível")
            
            # Calcular período
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            # Buscar movimentações
            movimentacoes_data = self._get_movements_data_optimized(start_date, end_date)
            
            # Calcular estatísticas
            stats = self._calculate_movement_stats(movimentacoes_data)
            
            context = {
                'movimentacoes': movimentacoes_data,
                'stats': stats,
                'start_date': start_date,
                'end_date': end_date,
                'generated_at': timezone.now(),
                'user': request.user,
                'title': 'Relatório de Movimentações',
                'company_name': 'Sistema de Farmácia',
                'report_type': 'movements',
            }
            
            if PDF_ENGINE == 'weasyprint':
                return self._generate_with_weasyprint(request, context, 'reports/pdf/movements_report.html')
            else:
                return self._generate_with_reportlab_movements(context)
                
        except Exception as e:
            logger.error(f"Erro na geração do PDF de movimentações: {str(e)}", exc_info=True)
            return self._generate_error_pdf("Relatório de Movimentações", str(e))
    
    def generate_expiration_report_pdf(self, request: HttpRequest) -> HttpResponse:
        """
        Gerar relatório de vencimentos em PDF
        """
        logger.info("Iniciando geração do relatório de vencimentos")
        
        try:
            if not PDF_ENGINE:
                raise PDFGenerationError("Nenhuma biblioteca PDF disponível")
            
            # Calcular datas limite
            today = timezone.now().date()
            thirty_days = today + timedelta(days=30)
            
            # Buscar dados de vencimento
            vencimentos_data = self._get_expiration_data_optimized(today, thirty_days)
            
            context = {
                'vencimentos': vencimentos_data,
                'today': today,
                'thirty_days_limit': thirty_days,
                'generated_at': timezone.now(),
                'user': request.user,
                'title': 'Relatório de Vencimentos',
                'company_name': 'Sistema de Farmácia',
                'report_type': 'expiration',
            }
            
            if PDF_ENGINE == 'weasyprint':
                return self._generate_with_weasyprint(request, context, 'reports/pdf/expiration_report.html')
            else:
                return self._generate_with_reportlab_expiration(context)
                
        except Exception as e:
            logger.error(f"Erro na geração do PDF de vencimentos: {str(e)}", exc_info=True)
            return self._generate_error_pdf("Relatório de Vencimentos", str(e))
    
    def _get_stock_data_optimized(self) -> List[Dict]:
        """
        Buscar dados de estoque com queries otimizadas (sem lotes)
        """
        logger.debug("Buscando dados de estoque otimizados")
        
        try:
            from apps.branches.models import BranchStock
            from apps.inventory.models import Medication
            
            # Query otimizada usando BranchStock
            medications = Medication.objects.select_related(
                'category'
            ).prefetch_related(
                'branchstock_set'
            ).annotate(
                total_quantity=Sum('branchstock__quantity'),
                total_reserved=Sum('branchstock__reserved_quantity')
            ).filter(
                is_active=True
            ).order_by('name')
            
            # Converter para lista de dicts
            result = []
            for med in medications:
                available = (med.total_quantity or 0) - (med.total_reserved or 0)
                
                result.append({
                    'name': med.name,
                    'category': med.category.name if med.category else 'N/A',
                    'total_quantity': med.total_quantity or 0,
                    'total_reserved': med.total_reserved or 0,
                    'available_quantity': available,
                    'minimum_stock': med.minimum_stock,
                    'status': 'normal',
                    'is_low_stock': available <= med.minimum_stock if med.minimum_stock else False,
                })
            
            logger.debug(f"Dados de estoque coletados: {len(result)} medicamentos")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de estoque: {str(e)}")
            return []
    
    def _calculate_stock_metrics(self, medicamentos_data: List[Dict]) -> Dict:
        """
        Calcular métricas consolidadas do estoque
        """
        total_medications = len(medicamentos_data)
        total_stock = sum(med['total_quantity'] for med in medicamentos_data)
        total_available = sum(med['available_quantity'] for med in medicamentos_data)
        total_reserved = sum(med['total_reserved'] for med in medicamentos_data)
        
        expired_medications = sum(1 for med in medicamentos_data if med['status'] == 'expired')
        near_expiry_medications = sum(1 for med in medicamentos_data if med['status'] == 'near_expiry')
        low_stock_medications = sum(1 for med in medicamentos_data if med['is_low_stock'])
        
        return {
            'total_medications': total_medications,
            'total_stock': total_stock,
            'total_available': total_available,
            'total_reserved': total_reserved,
            'expired_medications': expired_medications,
            'near_expiry_medications': near_expiry_medications,
            'low_stock_medications': low_stock_medications,
        }
    
    def _get_movements_data_optimized(self, start_date, end_date) -> List[Dict]:
        """
        Buscar dados de movimentações com filtro de data
        """
        logger.debug(f"Buscando movimentações de {start_date} até {end_date}")
        
        try:
            # Como não temos modelo de movimentação específico ainda,
            # vou simular com transferências de estoque
            from apps.branches.models import StockTransfer
            
            transfers = StockTransfer.objects.select_related(
                'medication',
                'from_branch',
                'to_branch',
                'requested_by'
            ).filter(
                requested_at__range=[start_date, end_date]
            ).order_by('-requested_at')
            
            result = []
            for transfer in transfers:
                result.append({
                    'date': transfer.requested_at,
                    'type': 'transfer',
                    'medication_name': transfer.medication.name,
                    'quantity': transfer.quantity,
                    'from_location': transfer.from_branch.name if transfer.from_branch else 'Estoque Geral',
                    'to_location': transfer.to_branch.name if transfer.to_branch else 'Estoque Geral',
                    'user': transfer.requested_by.get_full_name() or transfer.requested_by.username,
                    'status': transfer.get_status_display(),
                })
            
            logger.debug(f"Movimentações coletadas: {len(result)} registros")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar movimentações: {str(e)}")
            return []
    
    def _calculate_movement_stats(self, movimentacoes_data: List[Dict]) -> Dict:
        """
        Calcular estatísticas das movimentações
        """
        total_movements = len(movimentacoes_data)
        total_quantity = sum(mov['quantity'] for mov in movimentacoes_data)
        
        # Contar por status
        completed = sum(1 for mov in movimentacoes_data if mov['status'] == 'Aprovado')
        pending = sum(1 for mov in movimentacoes_data if mov['status'] == 'Pendente')
        rejected = sum(1 for mov in movimentacoes_data if mov['status'] == 'Rejeitado')
        
        return {
            'total_movements': total_movements,
            'total_quantity': total_quantity,
            'completed_movements': completed,
            'pending_movements': pending,
            'rejected_movements': rejected,
        }
    
    def _get_expiration_data_optimized(self, today, thirty_days_limit) -> Dict:
        """
        Buscar dados de vencimento otimizados (sem lotes)
        """
        logger.debug(f"Buscando dados de vencimento até {thirty_days_limit}")
        
        try:
            from apps.inventory.models import Stock
            
            # Estoque vencido
            expired_stocks = Stock.objects.select_related(
                'medication', 'medication__category'
            ).filter(
                is_active=True,
                expiry_date__lt=today
            ).order_by('expiry_date')
            
            # Estoque próximo ao vencimento
            near_expiry_stocks = Stock.objects.select_related(
                'medication', 'medication__category'
            ).filter(
                is_active=True,
                expiry_date__gte=today,
                expiry_date__lte=thirty_days_limit
            ).order_by('expiry_date')
            
            # Converter para formato otimizado
            expired_data = []
            for stock in expired_stocks:
                if stock.quantity > 0:
                    expired_data.append({
                        'medication_name': stock.medication.name,
                        'category': stock.medication.category.name if stock.medication.category else 'N/A',
                        'expiry_date': stock.expiry_date,
                        'total_quantity': stock.quantity,
                        'days_expired': (today - stock.expiry_date).days,
                    })
            
            near_expiry_data = []
            for stock in near_expiry_stocks:
                if stock.quantity > 0:
                    near_expiry_data.append({
                        'medication_name': stock.medication.name,
                        'category': stock.medication.category.name if stock.medication.category else 'N/A',
                        'expiry_date': stock.expiry_date,
                        'total_quantity': stock.quantity,
                        'days_until_expiry': (stock.expiry_date - today).days,
                    })
            
            return {
                'expired': expired_data,
                'near_expiry': near_expiry_data,
                'expired_count': len(expired_data),
                'near_expiry_count': len(near_expiry_data),
                'total_expired_quantity': sum(item['total_quantity'] for item in expired_data),
                'total_near_expiry_quantity': sum(item['total_quantity'] for item in near_expiry_data),
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de vencimento: {str(e)}")
            return {
                'expired': [],
                'near_expiry': [],
                'expired_count': 0,
                'near_expiry_count': 0,
                'total_expired_quantity': 0,
                'total_near_expiry_quantity': 0,
            }
    
    def _generate_with_weasyprint(self, request: HttpRequest, context: Dict, template_name: str) -> HttpResponse:
        """
        Gerar PDF usando WeasyPrint (engine preferida)
        """
        logger.debug(f"Gerando PDF com WeasyPrint - template: {template_name}")
        
        try:
            # Renderizar HTML
            html_string = render_to_string(template_name, context)
            
            # CSS otimizado para PDF
            css_content = self._get_pdf_css(context['report_type'])
            css = CSS(string=css_content, font_config=self.font_config)
            
            # Gerar PDF
            html_doc = HTML(
                string=html_string,
                base_url=request.build_absolute_uri()
            )
            
            pdf_buffer = io.BytesIO()
            html_doc.write_pdf(
                pdf_buffer,
                stylesheets=[css],
                font_config=self.font_config
            )
            
            # Preparar response
            pdf_buffer.seek(0)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            
            # Nome do arquivo com timestamp
            timestamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')
            filename = f"{context['report_type']}_{timestamp}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"PDF gerado com sucesso: {filename}")
            return response
            
        except Exception as e:
            logger.error(f"Erro no WeasyPrint: {str(e)}")
            raise PDFGenerationError(f"Falha na geração com WeasyPrint: {str(e)}")
    
    def _get_pdf_css(self, report_type: str) -> str:
        """
        CSS otimizado para diferentes tipos de relatório
        """
        base_css = """
        @page {
            size: A4;
            margin: 2cm 1.5cm;
            @top-center { 
                content: "Sistema de Farmácia - """ + report_type.title() + """"; 
                font-size: 10pt;
                color: #666;
            }
            @bottom-center { 
                content: "Página " counter(page) " de " counter(pages); 
                font-size: 9pt;
                color: #666;
            }
        }
        
        * {
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'DejaVu Sans', Arial, sans-serif; 
            font-size: 10pt; 
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 2px solid #007bff;
            padding-bottom: 15px;
        }
        
        .header h1 {
            font-size: 18pt;
            margin: 0 0 10px 0;
            color: #007bff;
        }
        
        .header h2 {
            font-size: 14pt;
            margin: 0 0 5px 0;
            color: #333;
        }
        
        .header .meta {
            font-size: 9pt;
            color: #666;
        }
        
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 15px; 
            margin-bottom: 30px; 
        }
        
        .metric-card { 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 5px;
            text-align: center;
            background: #f8f9fa;
        }
        
        .metric-card h3 {
            font-size: 9pt;
            margin: 0 0 5px 0;
            color: #666;
            text-transform: uppercase;
        }
        
        .metric-card .value {
            font-size: 14pt;
            font-weight: bold;
            color: #007bff;
            margin: 0;
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
            font-size: 9pt;
        }
        
        th, td { 
            border: 1px solid #ddd; 
            padding: 6px 8px; 
            text-align: left; 
            vertical-align: top;
        }
        
        th { 
            background-color: #f8f9fa; 
            font-weight: bold;
            color: #333;
            font-size: 8pt;
            text-transform: uppercase;
        }
        
        .status-expired { 
            background-color: #ffebee !important; 
            color: #c62828 !important; 
        }
        
        .status-near-expiry { 
            background-color: #fff8e1 !important; 
            color: #f57c00 !important; 
        }
        
        .status-normal { 
            background-color: #e8f5e8 !important; 
            color: #2e7d32 !important; 
        }
        
        .text-center { text-align: center; }
        .text-right { text-align: right; }
        .font-bold { font-weight: bold; }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }
        
        .page-break { page-break-before: always; }
        
        /* Specific styles for different report types */
        """
        
        if report_type == 'stock':
            base_css += """
            .low-stock { background-color: #fff3cd !important; }
            """
        elif report_type == 'movements':
            base_css += """
            .movement-in { color: #28a745; }
            .movement-out { color: #dc3545; }
            """
        elif report_type == 'expiration':
            base_css += """
            .critical { background-color: #f8d7da !important; }
            .warning { background-color: #fff3cd !important; }
            """
        
        return base_css
    
    def _generate_error_pdf(self, report_title: str, error_message: str) -> HttpResponse:
        """
        Gerar PDF de erro quando a geração principal falha
        """
        logger.warning(f"Gerando PDF de erro para: {report_title}")
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            
            # Header
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, "ERRO NA GERAÇÃO DO RELATÓRIO")
            
            # Error details
            p.setFont("Helvetica", 12)
            p.drawString(100, 700, f"Relatório: {report_title}")
            p.drawString(100, 670, f"Data: {timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Error message (wrapped)
            p.setFont("Helvetica", 10)
            y_position = 630
            lines = self._wrap_text(f"Erro: {error_message}", 60)
            for line in lines:
                p.drawString(100, y_position, line)
                y_position -= 15
            
            # Support message
            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, y_position - 30, "Entre em contato com o suporte técnico.")
            
            p.save()
            
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="erro_relatorio.pdf"'
            
            return response
            
        except Exception as e:
            logger.critical(f"Falha catastrófica na geração de PDF de erro: {str(e)}")
            return HttpResponse(
                f"Erro crítico na geração de PDF: {str(e)}", 
                status=500,
                content_type='text/plain'
            )
    
    def _wrap_text(self, text: str, line_length: int) -> List[str]:
        """
        Quebrar texto em linhas para PDFs simples
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > line_length:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _generate_with_reportlab_stock(self, context: Dict) -> HttpResponse:
        """
        Gerar PDF de estoque usando ReportLab (fallback)
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 50, context.get('title', 'Relatório de Estoque'))
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 70, f"Gerado em: {timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')}")
        c.drawString(30, height - 85, f"Usuário: {getattr(context.get('user'), 'username', 'N/A')}")

        # Métricas
        metrics = context.get('metrics', {})
        y = height - 110
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Resumo do Estoque")
        y -= 18
        c.setFont("Helvetica", 10)
        for label, key in [
            ("Total de Medicamentos", 'total_medications'),
            ("Total em Estoque", 'total_stock'),
            ("Quantidade Disponível", 'total_available'),
            ("Quantidade Reservada", 'total_reserved'),
            ("Medicamentos Vencidos", 'expired_medications'),
            ("Medicamentos Próximos ao Vencimento", 'near_expiry_medications'),
            ("Medicamentos com Baixo Estoque", 'low_stock_medications'),
        ]:
            c.drawString(30, y, f"{label}: {metrics.get(key, 0)}")
            y -= 14

        # Tabela simples de medicamentos (top 100)
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30, y, "Medicamentos")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(30, y, "Nome")
        c.drawString(200, y, "Categoria")
        c.drawString(320, y, "Total")
        c.drawString(370, y, "Reservado")
        c.drawString(430, y, "Disponível")
        c.drawString(500, y, "Status")
        y -= 12
        c.line(28, y, width - 28, y)
        y -= 8

        for med in context.get('medicamentos', [])[:100]:
            if y < 80:
                c.showPage()
                y = height - 60
            c.setFont("Helvetica", 9)
            c.drawString(30, y, str(med.get('name', ''))[:28])
            c.drawString(200, y, str(med.get('category', 'N/A'))[:18])
            c.drawRightString(355, y, str(med.get('total_quantity', 0)))
            c.drawRightString(415, y, str(med.get('total_reserved', 0)))
            c.drawRightString(485, y, str(med.get('available_quantity', 0)))
            c.drawString(500, y, str(med.get('status', 'normal')))
            y -= 12

        c.showPage()
        c.save()
        buffer.seek(0)

        timestamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_{timestamp}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _generate_with_reportlab_movements(self, context: Dict) -> HttpResponse:
        """
        Gerar PDF de movimentações usando ReportLab (fallback)
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 50, context.get('title', 'Relatório de Movimentações'))
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 70, f"Período: {context.get('start_date')} até {context.get('end_date')}")
        c.drawString(30, height - 85, f"Gerado em: {timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')}")

        # Estatísticas
        stats = context.get('stats', {})
        y = height - 110
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Resumo das Movimentações")
        y -= 18
        c.setFont("Helvetica", 10)
        for label, key in [
            ("Total de Movimentações", 'total_movements'),
            ("Quantidade Total", 'total_quantity'),
            ("Aprovadas", 'completed_movements'),
            ("Pendentes", 'pending_movements'),
            ("Rejeitadas", 'rejected_movements'),
        ]:
            c.drawString(30, y, f"{label}: {stats.get(key, 0)}")
            y -= 14

        # Lista simples (top 200)
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30, y, "Movimentações")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(30, y, "Data")
        c.drawString(130, y, "Medicamento")
        c.drawRightString(300, y, "Qtd")
        c.drawString(330, y, "De")
        c.drawString(430, y, "Para")
        c.drawString(530, y, "Status")
        y -= 12
        c.line(28, y, width - 28, y)
        y -= 8

        for mov in context.get('movimentacoes', [])[:200]:
            if y < 80:
                c.showPage()
                y = height - 60
            c.setFont("Helvetica", 9)
            date_str = getattr(mov.get('date'), 'strftime', lambda x: str(mov.get('date')))("%d/%m/%Y %H:%M") if mov.get('date') else ""
            c.drawString(30, y, date_str)
            c.drawString(130, y, str(mov.get('medication_name', ''))[:24])
            c.drawRightString(300, y, str(mov.get('quantity', 0)))
            c.drawString(330, y, str(mov.get('from_location', ''))[:18])
            c.drawString(430, y, str(mov.get('to_location', ''))[:18])
            c.drawString(530, y, str(mov.get('status', ''))) 
            y -= 12

        c.showPage()
        c.save()
        buffer.seek(0)

        timestamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')
        filename = f"movements_{timestamp}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _generate_with_reportlab_expiration(self, context: Dict) -> HttpResponse:
        """
        Gerar PDF de vencimentos usando ReportLab (fallback)
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 50, context.get('title', 'Relatório de Vencimentos'))
        c.setFont("Helvetica", 10)
        c.drawString(30, height - 70, f"Data: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")

        y = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Lotes Vencidos")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(30, y, "Medicamento")
        c.drawString(300, y, "Categoria")
        c.drawString(420, y, "Qtde")
        c.drawString(470, y, "Vencimento")
        y -= 12
        c.line(28, y, width - 28, y)
        y -= 8

        for item in context.get('vencimentos', {}).get('expired', [])[:100]:
            if y < 80:
                c.showPage()
                y = height - 60
            c.setFont("Helvetica", 9)
            c.drawString(30, y, str(item.get('medication_name', ''))[:40])
            c.drawString(300, y, str(item.get('category', ''))[:18])
            c.drawRightString(450, y, str(item.get('total_quantity', 0)))
            c.drawString(470, y, str(item.get('expiry_date', '')))
            y -= 12

        # Próximos ao vencimento
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y, "Medicamentos Próximos ao Vencimento")
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(30, y, "Medicamento")
        c.drawString(300, y, "Categoria")
        c.drawString(420, y, "Qtde")
        c.drawString(470, y, "Vencimento")
        y -= 12
        c.line(28, y, width - 28, y)
        y -= 8

        for item in context.get('vencimentos', {}).get('near_expiry', [])[:100]:
            if y < 80:
                c.showPage()
                y = height - 60
            c.setFont("Helvetica", 9)
            c.drawString(30, y, str(item.get('medication_name', ''))[:40])
            c.drawString(300, y, str(item.get('category', ''))[:18])
            c.drawRightString(450, y, str(item.get('total_quantity', 0)))
            c.drawString(470, y, str(item.get('expiry_date', '')))
            y -= 12

        c.showPage()
        c.save()
        buffer.seek(0)

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"expiration_{timestamp}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# Instância global do gerador
pdf_generator = PDFGenerator()
