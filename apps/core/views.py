# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.db import models
from django.utils import timezone
# MedicationBatch e BatchLocation foram removidos
from apps.inventory.models import Medication
from apps.branches.models import Branch
from apps.authentication.decorators import farmaceutico_required, admin_required


@login_required
def dashboard(request):
    """
    Dashboard principal do sistema
    Mostra estatísticas gerais e links para as seções principais
    """
    from apps.branches.models import BranchStock
    
    # Medicamentos únicos
    total_medications = Medication.objects.filter(is_active=True).count()
    
    # Filiais ativas
    total_branches = Branch.objects.filter(is_active=True).count()
    
    # Quantidade total em estoque (por filiais)
    total_quantity = BranchStock.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Estatísticas de estoque baixo
    low_stock_count = BranchStock.objects.filter(
        quantity__lte=models.F('medication__minimum_stock')
    ).count()
    
    context = {
        'total_medications': total_medications,
        'total_branches': total_branches,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'critical_alerts': [],
    }
    
    return render(request, 'core/dashboard.html', context)


# @farmaceutico_required
# def unified_stock_view(request):
#     """
#     DEPRECADO: Página unificada de lotes removida após reset total do esquema.
#     """
#     return redirect('branches:branch_list')
    
    context = {
        'locations': locations_list,
        'categories': categories,
        'branches': branches,
        'search': search,
        'selected_category': category,
        'selected_location_type': location_type,
        'selected_branch_id': branch_id,
        'expiry_status': expiry_status,
        'low_stock_only': low_stock_only,
        'total_batches': total_batches,
        'total_locations': total_locations,
        'expired_batches': expired_batches,
        'near_expiry_batches': near_expiry_batches,
        'expiry_status_choices': [
            ('', 'Todos os status'),
            ('normal', 'Normal'),
            ('near_expiry', 'Próximo ao Vencimento'),
            ('expired', 'Vencido')
        ],
        'location_type_choices': [
            ('', 'Todas as localizações'),
            ('general', 'Estoque Geral'),
            ('branch', 'Filiais')
        ]
    }
    
    # return render(request, 'core/unified_stock.html', context)


# View batch_detail_view foi removida - funcionalidade de lotes removida


# View location_stock_view foi removida - funcionalidade de lotes removida
@farmaceutico_required
def location_stock_view(request, location_type, location_id=None):
    """Redireciona para dashboard de filiais"""
    return redirect('branches:dashboard')


# View batch_consistency_report foi removida - funcionalidade de lotes removida


# API Endpoints para integração

# Views api_batch_locations e api_medication_batches foram removidas
# Funcionalidade de lotes removida do sistema


# View complete_stock_view foi removida - funcionalidade de lotes removida
# Redireciona para dashboard de filiais
@farmaceutico_required
def complete_stock_view(request):
    """Redireciona para o dashboard de filiais"""
    from django.shortcuts import redirect
    return redirect('branches:dashboard')


@admin_required
def system_integrity_view(request):
    """
    Vista de integridade do sistema
    Versão simplificada sem referências a lotes
    """
    from apps.branches.models import BranchStock
    from apps.inventory.models import Medication
    
    # Verificações básicas de integridade
    total_medications = Medication.objects.filter(is_active=True).count()
    total_stocks = BranchStock.objects.count()
    
    # Status geral do sistema
    system_health = 'healthy'
    issues = []
    
    context = {
        'total_medications': total_medications,
        'total_stocks': total_stocks,
        'system_health': system_health,
        'issues': issues,
    }
    
    return render(request, 'core/system_integrity.html', context)


@login_required
def estoque_redirect(request):
    """Redireciona para a lista de filiais, novo fluxo de estoque agregado."""
    return redirect('branches:branch_list')