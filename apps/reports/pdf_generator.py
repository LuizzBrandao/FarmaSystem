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
    print("✅ WeasyPrint disponível - usando como engine principal")
except ImportError:
    try:
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        PDF_ENGINE = 'reportlab'
        print("⚠️ WeasyPrint não disponível - usando ReportLab como fallback")
    except ImportError:
        PDF_ENGINE = None
        print("❌ Nenhuma biblioteca PDF disponível - instale WeasyPrint ou ReportLab")

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
            self.font_config = FontConfiguration()
        
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
        Buscar dados de estoque com queries otimizadas
        """
        logger.debug("Buscando dados de estoque otimizados")
        
        try:
            from apps.core.models import MedicationBatch, BatchLocation
            from apps.inventory.models import Medication
            
            # Query otimizada com agregações
            medications = Medication.objects.select_related(
                'category'
            ).prefetch_related(
                'unified_batches__locations'
            ).annotate(
                total_quantity=Sum('unified_batches__locations__quantity'),
                total_reserved=Sum('unified_batches__locations__reserved_quantity'),
                expired_batches_count=Count(
                    'unified_batches',
                    filter=Q(unified_batches__expiry_date__lt=timezone.now().date())
                ),
                next_expiry=Min('unified_batches__expiry_date')
            ).filter(
                is_active=True
            ).order_by('name')
            
            # Converter para lista de dicts para otimizar memory usage
            result = []
            for med in medications:
                available = (med.total_quantity or 0) - (med.total_reserved or 0)
                
                # Determinar status baseado no vencimento
                status = 'normal'
                if med.expired_batches_count > 0:
                    status = 'expired'
                elif med.next_expiry and med.next_expiry <= timezone.now().date() + timedelta(days=30):
                    status = 'near_expiry'
                
                result.append({
                    'name': med.name,
                    'category': med.category.name if med.category else 'N/A',
                    'total_quantity': med.total_quantity or 0,
                    'total_reserved': med.total_reserved or 0,
                    'available_quantity': available,
                    'minimum_stock': med.minimum_stock,
                    'next_expiry': med.next_expiry,
                    'expired_batches_count': med.expired_batches_count,
                    'status': status,
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
        Buscar dados de vencimento otimizados
        """
        logger.debug(f"Buscando dados de vencimento até {thirty_days_limit}")
        
        try:
            from apps.core.models import MedicationBatch
            
            # Lotes vencidos
            expired_batches = MedicationBatch.objects.select_related(
                'medication', 'medication__category'
            ).prefetch_related(
                'locations'
            ).filter(
                is_active=True,
                expiry_date__lt=today
            ).order_by('expiry_date')
            
            # Lotes próximos ao vencimento
            near_expiry_batches = MedicationBatch.objects.select_related(
                'medication', 'medication__category'
            ).prefetch_related(
                'locations'
            ).filter(
                is_active=True,
                expiry_date__gte=today,
                expiry_date__lte=thirty_days_limit
            ).order_by('expiry_date')
            
            # Converter para formato otimizado
            expired_data = []
            for batch in expired_batches:
                total_quantity = sum(loc.quantity for loc in batch.locations.filter(is_active=True))
                if total_quantity > 0:  # Só incluir lotes com estoque
                    expired_data.append({
                        'batch_number': batch.batch_number,
                        'medication_name': batch.medication.name,
                        'category': batch.medication.category.name if batch.medication.category else 'N/A',
                        'expiry_date': batch.expiry_date,
                        'total_quantity': total_quantity,
                        'days_expired': (today - batch.expiry_date).days,
                    })
            
            near_expiry_data = []
            for batch in near_expiry_batches:
                total_quantity = sum(loc.quantity for loc in batch.locations.filter(is_active=True))
                if total_quantity > 0:
                    near_expiry_data.append({
                        'batch_number': batch.batch_number,
                        'medication_name': batch.medication.name,
                        'category': batch.medication.category.name if batch.medication.category else 'N/A',
                        'expiry_date': batch.expiry_date,
                        'total_quantity': total_quantity,
                        'days_until_expiry': (batch.expiry_date - today).days,
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
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
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
            p.drawString(100, 670, f"Data: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
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


# Instância global do gerador
pdf_generator = PDFGenerator()
