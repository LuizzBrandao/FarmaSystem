from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import logging

from .models import Report
from .pdf_generator import pdf_generator, PDFGenerationError
from apps.authentication.decorators import farmaceutico_required, admin_required

# Logger para views de relatórios
logger = logging.getLogger(__name__)


@login_required
def report_list(request):
    """Lista de relatórios"""
    reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')
    context = {'reports': reports}
    return render(request, 'reports/report_list.html', context)


@login_required
def report_generate(request):
    """Gerar novo relatório"""
    if request.method == 'POST':
        # Lógica para gerar relatório
        messages.success(request, 'Relatório gerado com sucesso!')
        return redirect('reports:report_list')
    
    return render(request, 'reports/report_generate.html')


@login_required
def report_detail(request, pk):
    """Detalhes do relatório"""
    report = get_object_or_404(Report, pk=pk)
    context = {'report': report}
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_download(request, pk):
    """Download do relatório"""
    report = get_object_or_404(Report, pk=pk)
    # Lógica para download
    return HttpResponse("Download do relatório em desenvolvimento")


# ===============================
# 📊 VIEWS ROBUSTAS PARA GERAÇÃO DE PDFs
# ===============================

@farmaceutico_required
@require_http_methods(["GET"])
def stock_report_pdf(request):
    """
    Gerar relatório de estoque em PDF - Nova implementação robusta
    """
    logger.info(f"Usuário {request.user.username} solicitou relatório de estoque PDF")
    
    try:
        # Usar o gerador robusto
        response = pdf_generator.generate_stock_report_pdf(request)
        
        # Registrar no banco apenas se geração foi bem-sucedida
        try:
            Report.objects.create(
                title=f"Relatório de Estoque - {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
                report_type='stock',
                generated_by=request.user,
                description="Relatório completo de estoque com métricas consolidadas",
                status='completed'
            )
        except Exception as db_error:
            logger.warning(f"Erro ao registrar relatório no banco: {db_error}")
            # Não falhar a resposta por causa do registro
        
        logger.info(f"Relatório de estoque gerado com sucesso para {request.user.username}")
        return response
        
    except PDFGenerationError as e:
        logger.error(f"Erro na geração do PDF de estoque: {str(e)}")
        messages.error(request, f"Erro ao gerar relatório: {str(e)}")
        return redirect('reports:report_list')
    except Exception as e:
        logger.error(f"Erro inesperado na geração do PDF de estoque: {str(e)}", exc_info=True)
        messages.error(request, "Erro inesperado ao gerar relatório. Tente novamente.")
        return redirect('reports:report_list')


@farmaceutico_required
@require_http_methods(["GET"])
def movements_report_pdf(request):
    """
    Gerar relatório de movimentações em PDF - Nova implementação robusta
    """
    logger.info(f"Usuário {request.user.username} solicitou relatório de movimentações PDF")
    
    try:
        # Usar o gerador robusto
        response = pdf_generator.generate_movements_report_pdf(request)
        
        # Registrar no banco
        try:
            Report.objects.create(
                title=f"Relatório de Movimentações - {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
                report_type='movements',
                generated_by=request.user,
                description="Relatório de movimentações dos últimos 30 dias",
                status='completed'
            )
        except Exception as db_error:
            logger.warning(f"Erro ao registrar relatório no banco: {db_error}")
        
        logger.info(f"Relatório de movimentações gerado com sucesso para {request.user.username}")
        return response
        
    except PDFGenerationError as e:
        logger.error(f"Erro na geração do PDF de movimentações: {str(e)}")
        messages.error(request, f"Erro ao gerar relatório: {str(e)}")
        return redirect('reports:report_list')
    except Exception as e:
        logger.error(f"Erro inesperado na geração do PDF de movimentações: {str(e)}", exc_info=True)
        messages.error(request, "Erro inesperado ao gerar relatório. Tente novamente.")
        return redirect('reports:report_list')


@farmaceutico_required
@require_http_methods(["GET"])
def expiration_report_pdf(request):
    """
    Gerar relatório de vencimentos em PDF - Nova implementação robusta
    """
    logger.info(f"Usuário {request.user.username} solicitou relatório de vencimentos PDF")
    
    try:
        # Usar o gerador robusto
        response = pdf_generator.generate_expiration_report_pdf(request)
        
        # Registrar no banco
        try:
            Report.objects.create(
                title=f"Relatório de Vencimentos - {timezone.localtime().strftime('%d/%m/%Y %H:%M')}",
                report_type='expiration',
                generated_by=request.user,
                description="Relatório de lotes vencidos e próximos ao vencimento",
                status='completed'
            )
        except Exception as db_error:
            logger.warning(f"Erro ao registrar relatório no banco: {db_error}")
        
        logger.info(f"Relatório de vencimentos gerado com sucesso para {request.user.username}")
        return response
        
    except PDFGenerationError as e:
        logger.error(f"Erro na geração do PDF de vencimentos: {str(e)}")
        messages.error(request, f"Erro ao gerar relatório: {str(e)}")
        return redirect('reports:report_list')
    except Exception as e:
        logger.error(f"Erro inesperado na geração do PDF de vencimentos: {str(e)}", exc_info=True)
        messages.error(request, "Erro inesperado ao gerar relatório. Tente novamente.")
        return redirect('reports:report_list')


# ===============================
# 🔧 API ENDPOINTS PARA FRONTEND
# ===============================

@farmaceutico_required
@require_http_methods(["GET"])
def pdf_status_check(request):
    """
    Verificar status do sistema de geração de PDFs
    """
    try:
        from .pdf_generator import PDF_ENGINE
        
        status = {
            'pdf_engine': PDF_ENGINE,
            'engine_available': PDF_ENGINE is not None,
            'timestamp': timezone.localtime().isoformat(),
        }
        
        if PDF_ENGINE == 'weasyprint':
            status['engine_name'] = 'WeasyPrint (Preferido)'
            status['engine_status'] = 'optimal'
        elif PDF_ENGINE == 'reportlab':
            status['engine_name'] = 'ReportLab (Fallback)'
            status['engine_status'] = 'functional'
        else:
            status['engine_name'] = 'Nenhum'
            status['engine_status'] = 'error'
        
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'engine_available': False,
            'engine_status': 'error'
        }, status=500)


# ===============================
# 📋 VIEWS EXISTENTES MANTIDAS
# ===============================

# Manter compatibilidade com views antigas para backwards compatibility
def stock_report(request):
    """Redirecionamento para nova implementação"""
    return stock_report_pdf(request)

def movement_report(request):
    """Redirecionamento para nova implementação"""
    return movements_report_pdf(request)

def expiry_report(request):
    """Redirecionamento para nova implementação"""
    return expiration_report_pdf(request)