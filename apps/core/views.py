from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from .models import MedicationBatch, BatchLocation
from apps.inventory.models import Medication
from apps.branches.models import Branch
from apps.authentication.decorators import farmaceutico_required, admin_required


@login_required
def dashboard(request):
    """
    Dashboard principal do sistema
    Mostra estatísticas gerais e links para as seções principais
    """
    
    # Estatísticas dos lotes unificados
    total_batches = MedicationBatch.objects.filter(is_active=True).count()
    total_locations = BatchLocation.objects.filter(is_active=True, quantity__gt=0).count()
    
    # Medicamentos únicos
    total_medications = Medication.objects.filter(is_active=True).count()
    
    # Filiais ativas
    total_branches = Branch.objects.filter(is_active=True).count()
    
    # Status de vencimento (usando estrutura unificada)
    all_batches = MedicationBatch.objects.filter(is_active=True)
    expired_count = sum(1 for batch in all_batches if batch.is_expired)
    near_expiry_count = sum(1 for batch in all_batches if batch.is_near_expiry)
    
    # Quantidade total em estoque
    total_quantity = BatchLocation.objects.filter(
        is_active=True
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Alertas críticos
    critical_alerts = []
    if expired_count > 0:
        critical_alerts.append({
            'type': 'expired',
            'count': expired_count,
            'message': f'{expired_count} lote(s) vencido(s)',
            'icon': 'fas fa-times-circle',
            'color': 'danger'
        })
    
    if near_expiry_count > 0:
        critical_alerts.append({
            'type': 'near_expiry',
            'count': near_expiry_count,
            'message': f'{near_expiry_count} lote(s) próximo(s) ao vencimento',
            'icon': 'fas fa-exclamation-triangle',
            'color': 'warning'
        })
    
    # Calcular lotes normais
    normal_count = total_batches - expired_count - near_expiry_count
    
    context = {
        'total_batches': total_batches,
        'total_locations': total_locations,
        'total_medications': total_medications,
        'total_branches': total_branches,
        'total_quantity': total_quantity,
        'expired_count': expired_count,
        'near_expiry_count': near_expiry_count,
        'normal_count': normal_count,
        'critical_alerts': critical_alerts,
    }
    
    return render(request, 'core/dashboard.html', context)


@farmaceutico_required
def unified_stock_view(request):
    """
    VIEW UNIFICADA - Mostra todos os lotes do sistema
    Substitui as views separadas de estoque geral e filiais
    """
    
    # Filtros
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    location_type = request.GET.get('location_type', '')  # 'general', 'branch', ou ''
    branch_id = request.GET.get('branch_id', '')
    expiry_status = request.GET.get('expiry_status', '')
    low_stock_only = request.GET.get('low_stock', False)
    
    # Query base com todas as localizações ativas
    locations = BatchLocation.objects.filter(
        is_active=True,
        quantity__gt=0
    ).select_related(
        'batch__medication',
        'batch__medication__category',
        'branch'
    ).prefetch_related('batch__locations')
    
    # Aplicar filtros
    if search:
        locations = locations.filter(batch__medication__name__icontains=search)
    
    if category:
        locations = locations.filter(batch__medication__category_id=category)
    
    if location_type:
        locations = locations.filter(location_type=location_type)
    
    if branch_id:
        locations = locations.filter(branch_id=branch_id)
    
    # Converter para lista para aplicar filtros complexos
    locations_list = list(locations)
    
    if expiry_status:
        locations_list = [
            loc for loc in locations_list 
            if loc.batch.expiry_status == expiry_status
        ]
    
    if low_stock_only:
        locations_list = [
            loc for loc in locations_list 
            if loc.is_low_stock
        ]
    
    # Buscar dados para filtros
    from apps.inventory.models import Category
    categories = Category.objects.all()
    branches = Branch.objects.filter(is_active=True)
    
    # Estatísticas gerais
    total_batches = MedicationBatch.objects.count()
    total_locations = BatchLocation.objects.filter(is_active=True, quantity__gt=0).count()
    expired_batches = sum(1 for loc in locations_list if loc.batch.is_expired)
    near_expiry_batches = sum(1 for loc in locations_list if loc.batch.is_near_expiry)
    
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
    
    return render(request, 'core/unified_stock.html', context)


@farmaceutico_required
def batch_detail_view(request, batch_number):
    """
    Detalhes completos de um lote específico
    Mostra todas as localizações e histórico
    """
    batch = get_object_or_404(MedicationBatch, batch_number=batch_number)
    
    # Todas as localizações deste lote
    locations = batch.locations.filter(is_active=True).select_related('branch')
    
    # Estatísticas do lote
    total_quantity = locations.aggregate(total=Sum('quantity'))['total'] or 0
    available_quantity = locations.aggregate(
        available=Sum(F('quantity') - F('reserved_quantity'))
    )['available'] or 0
    
    # Histórico de transferências (se existir)
    transfers = getattr(batch, 'transfers', None)
    if transfers:
        recent_transfers = transfers.order_by('-requested_at')[:10]
    else:
        recent_transfers = []
    
    context = {
        'batch': batch,
        'locations': locations,
        'total_quantity': total_quantity,
        'available_quantity': available_quantity,
        'recent_transfers': recent_transfers,
    }
    
    return render(request, 'core/batch_detail.html', context)


@farmaceutico_required
def location_stock_view(request, location_type, location_id=None):
    """
    Vista específica por localização (Estoque Geral ou Filial específica)
    Mantém compatibilidade com URLs existentes
    """
    
    # Validar localização
    if location_type == 'general':
        location_name = 'Estoque Geral'
        branch = None
    elif location_type == 'branch':
        if not location_id:
            return JsonResponse({'error': 'branch_id é obrigatório para filiais'}, status=400)
        branch = get_object_or_404(Branch, pk=location_id, is_active=True)
        location_name = branch.name
    else:
        return JsonResponse({'error': 'location_type inválido'}, status=400)
    
    # Buscar localizações
    locations_query = BatchLocation.objects.filter(
        location_type=location_type,
        is_active=True,
        quantity__gt=0
    ).select_related(
        'batch__medication',
        'batch__medication__category'
    )
    
    if location_type == 'branch':
        locations_query = locations_query.filter(branch_id=location_id)
    else:
        locations_query = locations_query.filter(branch__isnull=True)
    
    # Filtros (mesmo sistema da view unificada)
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    expiry_status = request.GET.get('expiry_status', '')
    low_stock_only = request.GET.get('low_stock', False)
    
    if search:
        locations_query = locations_query.filter(batch__medication__name__icontains=search)
    
    if category:
        locations_query = locations_query.filter(batch__medication__category_id=category)
    
    locations_list = list(locations_query)
    
    if expiry_status:
        locations_list = [
            loc for loc in locations_list 
            if loc.batch.expiry_status == expiry_status
        ]
    
    if low_stock_only:
        locations_list = [
            loc for loc in locations_list 
            if loc.is_low_stock
        ]
    
    # Buscar dados para filtros
    from apps.inventory.models import Category
    categories = Category.objects.all()
    
    # Estatísticas da localização
    total_medications = len(set(loc.batch.medication.id for loc in locations_list))
    total_quantity = sum(loc.quantity for loc in locations_list)
    expired_count = sum(1 for loc in locations_list if loc.batch.is_expired)
    near_expiry_count = sum(1 for loc in locations_list if loc.batch.is_near_expiry)
    
    context = {
        'location_type': location_type,
        'location_name': location_name,
        'branch': branch,
        'locations': locations_list,
        'categories': categories,
        'total_medications': total_medications,
        'total_quantity': total_quantity,
        'expired_count': expired_count,
        'near_expiry_count': near_expiry_count,
        'search': search,
        'selected_category': category,
        'expiry_status': expiry_status,
        'low_stock_only': low_stock_only,
        'expiry_status_choices': [
            ('', 'Todos os status'),
            ('normal', 'Normal'),
            ('near_expiry', 'Próximo ao Vencimento'),
            ('expired', 'Vencido')
        ]
    }
    
    return render(request, 'core/location_stock.html', context)


@admin_required
def batch_consistency_report(request):
    """
    Relatório de consistência dos lotes
    Identifica possíveis problemas na estrutura unificada
    """
    
    # Lotes sem localização
    orphan_batches = MedicationBatch.objects.filter(
        locations__isnull=True
    ).values('batch_number', 'medication__name')
    
    # Lotes com quantidade total diferente da inicial
    inconsistent_quantities = []
    for batch in MedicationBatch.objects.prefetch_related('locations'):
        total_in_locations = sum(
            loc.quantity for loc in batch.locations.filter(is_active=True)
        )
        if total_in_locations != batch.initial_quantity:
            inconsistent_quantities.append({
                'batch_number': batch.batch_number,
                'medication': batch.medication.name,
                'initial_quantity': batch.initial_quantity,
                'current_total': total_in_locations,
                'difference': total_in_locations - batch.initial_quantity
            })
    
    # Localizações com quantidade reservada maior que total
    invalid_reservations = BatchLocation.objects.filter(
        reserved_quantity__gt=F('quantity')
    ).select_related('batch__medication', 'branch')
    
    # Lotes duplicados por medicamento e data
    from django.db.models import Count
    potential_duplicates = MedicationBatch.objects.values(
        'medication', 'expiry_date'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    context = {
        'orphan_batches': list(orphan_batches),
        'inconsistent_quantities': inconsistent_quantities,
        'invalid_reservations': invalid_reservations,
        'potential_duplicates': potential_duplicates,
        'total_batches': MedicationBatch.objects.count(),
        'total_locations': BatchLocation.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'core/consistency_report.html', context)


# API Endpoints para integração

@farmaceutico_required
def api_batch_locations(request, batch_number):
    """API: Todas as localizações de um lote"""
    batch = get_object_or_404(MedicationBatch, batch_number=batch_number)
    
    locations_data = []
    for location in batch.locations.filter(is_active=True):
        locations_data.append({
            'location_type': location.location_type,
            'location_name': location.location_name,
            'branch_id': location.branch.id if location.branch else None,
            'quantity': location.quantity,
            'reserved_quantity': location.reserved_quantity,
            'available_quantity': location.available_quantity,
        })
    
    return JsonResponse({
        'batch_number': batch.batch_number,
        'medication': batch.medication.name,
        'expiry_date': batch.expiry_date.strftime('%Y-%m-%d'),
        'expiry_status': batch.expiry_status,
        'total_quantity': sum(loc['quantity'] for loc in locations_data),
        'locations': locations_data
    })


@farmaceutico_required
def api_medication_batches(request, medication_id):
    """API: Todos os lotes de um medicamento"""
    medication = get_object_or_404(Medication, pk=medication_id)
    
    batches_data = []
    for batch in medication.unified_batches.filter(is_active=True):
        total_quantity = sum(
            loc.quantity for loc in batch.locations.filter(is_active=True)
        )
        available_quantity = sum(
            loc.available_quantity for loc in batch.locations.filter(is_active=True)
        )
        
        batches_data.append({
            'batch_number': batch.batch_number,
            'expiry_date': batch.expiry_date.strftime('%Y-%m-%d'),
            'expiry_status': batch.expiry_status,
            'days_until_expiry': batch.days_until_expiry,
            'total_quantity': total_quantity,
            'available_quantity': available_quantity,
            'locations_count': batch.locations.filter(is_active=True).count()
        })
    
    return JsonResponse({
        'medication_id': medication.id,
        'medication_name': medication.name,
        'total_batches': len(batches_data),
        'batches': batches_data
    })


@farmaceutico_required
def complete_stock_view(request):
    """
    Vista consolidada principal do estoque (antigo Estoque Completo)
    Integra todas as funcionalidades: filtragem, busca, métricas e ações
    """
    
    # Parâmetros de filtro
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    location_filter = request.GET.get('location', 'all')
    category_filter = request.GET.get('category', 'all')
    
    # Base queryset otimizado
    batches = MedicationBatch.objects.filter(is_active=True).select_related(
        'medication', 'medication__category', 'created_by'
    ).prefetch_related(
        'locations__branch'
    )
    
    # Aplicar filtros de busca
    if search_query:
        batches = batches.filter(
            Q(batch_number__icontains=search_query) |
            Q(medication__name__icontains=search_query) |
            Q(supplier_reference__icontains=search_query)
        )
    
    # Aplicar filtro de categoria
    if category_filter != 'all':
        batches = batches.filter(medication__category_id=category_filter)
    
    # Aplicar filtro de localização
    if location_filter != 'all':
        if location_filter == 'general':
            batches = batches.filter(locations__location_type='general', locations__is_active=True)
        else:
            batches = batches.filter(
                locations__location_type='branch', 
                locations__branch_id=location_filter,
                locations__is_active=True
            )
    
    # Aplicar filtro de status (calculado dinamicamente)
    batches_list = list(batches.distinct())
    
    if status_filter != 'all':
        if status_filter == 'expired':
            batches_list = [batch for batch in batches_list if batch.is_expired]
        elif status_filter == 'near_expiry':
            batches_list = [batch for batch in batches_list if batch.is_near_expiry]
        elif status_filter == 'normal':
            batches_list = [batch for batch in batches_list if not batch.is_expired and not batch.is_near_expiry]
    
    # Ordenar por data de vencimento e nome do medicamento
    batches_list.sort(key=lambda b: (b.expiry_date, b.medication.name))
    
    # Calcular métricas dos cards
    total_batches = len(batches_list)
    expired_count = sum(1 for batch in batches_list if batch.is_expired)
    near_expiry_count = sum(1 for batch in batches_list if batch.is_near_expiry)
    normal_count = total_batches - expired_count - near_expiry_count
    
    # Quantidade total no sistema (considerando filtros)
    if batches_list:
        batch_ids = [batch.id for batch in batches_list]
        total_quantity = BatchLocation.objects.filter(
            batch_id__in=batch_ids,
            is_active=True
        ).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        total_quantity = 0
    
    # Buscar categorias e localizações para os filtros
    from apps.inventory.models import Category
    from apps.branches.models import Branch
    
    categories = Category.objects.all().order_by('name')
    branches = Branch.objects.filter(is_active=True).order_by('name')
    
    context = {
        # Dados principais
        'batches': batches_list,
        'categories': categories,
        'branches': branches,
        
        # Métricas para os cards
        'total_batches': total_batches,
        'expired_count': expired_count,
        'near_expiry_count': near_expiry_count,
        'normal_count': normal_count,
        'total_quantity': total_quantity,
        
        # Filtros ativos
        'search_query': search_query,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'category_filter': category_filter,
        
        # Opções de filtro
        'status_choices': [
            ('all', 'Todos os Status'),
            ('normal', 'Normal'),
            ('near_expiry', 'Próximo Vencimento'),
            ('expired', 'Vencido')
        ],
        
        # Metadata
        'title': 'Estoque',
        'page_description': 'Vista consolidada de todos os lotes do sistema',
    }
    
    return render(request, 'core/estoque.html', context)


@admin_required
def system_integrity_view(request):
    """
    Vista de integridade do sistema
    Versão simplificada do relatório de consistência
    """
    
    # Verificações básicas de integridade
    total_batches = MedicationBatch.objects.count()
    total_locations = BatchLocation.objects.filter(is_active=True).count()
    
    # Lotes sem localização
    orphan_batches = MedicationBatch.objects.filter(
        locations__isnull=True
    ).count()
    
    # Localizações com quantidade inválida
    invalid_locations = BatchLocation.objects.filter(
        reserved_quantity__gt=F('quantity')
    ).count()
    
    # Status geral do sistema
    system_health = 'healthy'
    if orphan_batches > 0 or invalid_locations > 0:
        system_health = 'warning'
    
    issues = []
    if orphan_batches > 0:
        issues.append(f'{orphan_batches} lote(s) sem localização')
    if invalid_locations > 0:
        issues.append(f'{invalid_locations} localização(ões) com reserva inválida')
    
    context = {
        'total_batches': total_batches,
        'total_locations': total_locations,
        'orphan_batches': orphan_batches,
        'invalid_locations': invalid_locations,
        'system_health': system_health,
        'issues': issues,
    }
    
    return render(request, 'core/system_integrity.html', context)