# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
# -*- coding: utf-8 -*-
from .models import Branch, BranchStock, StockTransfer
# BranchMedicationBatch foi removido
from apps.inventory.models import Medication
from apps.authentication.decorators import farmaceutico_required, admin_required
from apps.notifications.services import NotificationManager


@login_required
def branch_list(request):
    """Lista de filiais"""
    branches = Branch.objects.filter(is_active=True).select_related('manager')
    context = {'branches': branches}
    return render(request, 'branches/branch_list.html', context)


@login_required
def branch_detail(request, pk):
    """Detalhes de uma filial específica - com cálculos sincronizados do banco"""
    branch = get_object_or_404(Branch, pk=pk)
    
    # Estatísticas da filial - calcular diretamente do banco para garantir sincronização
    branch_stocks = BranchStock.objects.filter(branch=branch).select_related('medication')
    
    # Calcular totais diretamente do banco (garantir sincronização)
    total_medications = branch_stocks.values('medication').distinct().count()
    total_stock_quantity = branch_stocks.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Medicamentos com estoque baixo
    low_stock_items = []
    for stock in branch_stocks:
        if stock.is_low_stock:
            low_stock_items.append(stock)
    
    # Transferências recentes
    from django.db import models
    recent_transfers = StockTransfer.objects.filter(
        models.Q(from_branch=branch) | models.Q(to_branch=branch)
    ).select_related('medication', 'from_branch', 'to_branch').order_by('-requested_at')[:10]
    
    context = {
        'branch': branch,
        'branch_stocks': branch_stocks,
        'low_stock_items': low_stock_items,
        'recent_transfers': recent_transfers,
        'total_medications': total_medications,  # Calculado diretamente do banco
        'total_stock': total_stock_quantity,  # Calculado diretamente do banco
        'low_stock_count': len(low_stock_items)
    }
    
    return render(request, 'branches/branch_detail.html', context)


@farmaceutico_required
def branch_stock_view(request, branch_pk):
    """Visualizar estoque de uma filial específica"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    
    # Filtros
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    low_stock_only = request.GET.get('low_stock', False)
    expiry_status = request.GET.get('expiry_status', '')
    
    # Buscar categorias para o filtro
    from apps.inventory.models import Category
    categories = Category.objects.all()
    
    # Query base
    stocks = BranchStock.objects.filter(branch=branch).select_related(
        'medication', 'medication__category'
    )
    
    # Aplicar filtros
    if search:
        stocks = stocks.filter(medication__name__icontains=search)
    
    if category:
        stocks = stocks.filter(medication__category_id=category)
    
    # Converter para lista para aplicar filtros complexos
    stocks_list = list(stocks)
    
    if low_stock_only:
        stocks_list = [stock for stock in stocks_list if stock.is_low_stock]
    
    if expiry_status:
        if expiry_status == 'expired':
            stocks_list = [stock for stock in stocks_list if stock.expiry_status == 'expired']
        elif expiry_status == 'near_expiry':
            stocks_list = [stock for stock in stocks_list if stock.expiry_status == 'near_expiry']
        elif expiry_status == 'normal':
            stocks_list = [stock for stock in stocks_list if stock.expiry_status == 'normal']
    
    context = {
        'branch': branch,
        'stocks': stocks_list,
        'categories': categories,
        'search': search,
        'selected_category': category,
        'low_stock_only': low_stock_only,
        'expiry_status': expiry_status,
        'expiry_status_choices': [
            ('', 'Todos os status'),
            ('normal', 'Normal'),
            ('near_expiry', 'Próximo ao Vencimento'),
            ('expired', 'Vencido')
        ]
    }
    
    return render(request, 'branches/branch_stock.html', context)


# View medication_batches_detail foi removida - funcionalidade de lotes removida
@farmaceutico_required
def medication_batches_detail(request, branch_pk, stock_pk):
    """Redireciona para o estoque da filial"""
    return redirect('branches:branch_stock', branch_pk=branch_pk)


@farmaceutico_required
def branch_expiry_dashboard(request, branch_pk):
    """Dashboard de vencimentos da filial - sem referências a lotes"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    
    # Buscar todos os stocks
    stocks = BranchStock.objects.filter(branch=branch).select_related(
        'medication', 'medication__category'
    )
    
    # Calcular estatísticas gerais
    total_medications = stocks.count()
    expired_medications = sum(1 for stock in stocks if stock.expiry_status == 'expired')
    near_expiry_medications = sum(1 for stock in stocks if stock.expiry_status == 'near_expiry')
    
    context = {
        'branch': branch,
        'total_medications': total_medications,
        'expired_medications': expired_medications,
        'near_expiry_medications': near_expiry_medications,
    }
    
    return render(request, 'branches/expiry_dashboard.html', context)


@farmaceutico_required
def update_branch_stock(request, branch_pk, medication_pk):
    """Atualizar estoque de um medicamento em uma filial"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    medication = get_object_or_404(Medication, pk=medication_pk)
    
    if request.method == 'POST':
        try:
            new_quantity = int(request.POST.get('quantity', 0))
            reason = request.POST.get('reason', '')
            
            # Obter ou criar estoque da filial
            branch_stock, created = BranchStock.objects.get_or_create(
                branch=branch,
                medication=medication,
                defaults={'quantity': 0}
            )
            
            old_quantity = branch_stock.quantity
            branch_stock.quantity = new_quantity
            branch_stock.save()
            
            # Verificar se precisa enviar alerta de estoque baixo
            if branch_stock.is_low_stock:
                notification_manager = NotificationManager()
                notification_manager.send_low_stock_alert(
                    branch, medication, new_quantity
                )
            
            messages.success(
                request,
                f'Estoque atualizado: {medication.name} de {old_quantity} para {new_quantity} unidades'
            )
            
        except ValueError:
            messages.error(request, 'Quantidade deve ser um número válido')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar estoque: {str(e)}')
    
    return redirect('branches:branch_stock', branch_pk=branch_pk)


@farmaceutico_required
def create_transfer(request):
    """Criar solicitação de transferência entre filiais com prevenção de duplicidade"""
    from django.db import transaction
    from django.db.models import F, Q
    
    if request.method == 'POST':
        try:
            from_branch_id = request.POST.get('from_branch')
            to_branch_id = request.POST.get('to_branch')
            transfer_all = request.POST.get('transfer_all') == 'on'
            reason = request.POST.get('reason', '')

            # Validações
            if from_branch_id == to_branch_id:
                messages.error(request, 'Filial de origem deve ser diferente da filial de destino')
                return redirect('branches:create_transfer')

            from_branch = get_object_or_404(Branch, pk=from_branch_id)
            to_branch = get_object_or_404(Branch, pk=to_branch_id)

            # Fluxo de transferência de todos os medicamentos
            if transfer_all:
                created_count = 0
                notification_manager = NotificationManager()
                
                with transaction.atomic():
                    # Itera por todos os estoques da filial de origem com lock
                    for from_stock in BranchStock.objects.select_for_update().select_related('medication').filter(branch=from_branch):
                        # Recalcular available_quantity após lock para garantir dados atualizados
                        available = max(0, from_stock.quantity - from_stock.reserved_quantity)
                        if available <= 0:
                            continue
                        
                        # Verificar se já existe transferência pendente para evitar duplicidade
                        existing_transfer = StockTransfer.objects.filter(
                            from_branch=from_branch,
                            to_branch=to_branch,
                            medication=from_stock.medication,
                            status='pending'
                        ).exists()
                        
                        if existing_transfer:
                            continue  # Pula se já existe transferência pendente
                        
                        # Cria transferência por medicamento
                        transfer = StockTransfer.objects.create(
                            from_branch=from_branch,
                            to_branch=to_branch,
                            medication=from_stock.medication,
                            quantity=available,
                            reason=reason or 'Transferência de todos os medicamentos',
                            requested_by=request.user
                        )
                        # Reserva estoque (usando update() para operação atômica)
                        BranchStock.objects.filter(pk=from_stock.pk).update(
                            reserved_quantity=F('reserved_quantity') + available
                        )
                        # Notificação
                        notification_manager.send_transfer_notification(transfer)
                        created_count += 1

                if created_count == 0:
                    messages.warning(request, 'Nenhum medicamento com quantidade disponível para transferir na filial de origem.')
                    return redirect('branches:create_transfer')

                messages.success(request, f'Solicitação criada: {created_count} transferências para todos os medicamentos disponíveis.')
                return redirect('branches:dashboard')

            # Fluxo de transferência individual (existente)
            medication_id = request.POST.get('medication')
            quantity = int(request.POST.get('quantity'))

            medication = get_object_or_404(Medication, pk=medication_id)

            with transaction.atomic():
                # Verificar se há estoque suficiente na filial de origem (com lock)
                try:
                    from_stock = BranchStock.objects.select_for_update().get(
                        branch=from_branch, 
                        medication=medication
                    )
                    
                    # Recalcular available_quantity após lock para garantir dados atualizados
                    available_qty = max(0, from_stock.quantity - from_stock.reserved_quantity)
                    
                    if available_qty < quantity:
                        messages.error(
                            request,
                            f'Estoque insuficiente. Disponível: {available_qty} unidades (Total: {from_stock.quantity}, Reservado: {from_stock.reserved_quantity})'
                        )
                        return redirect('branches:create_transfer')
                    
                    # Validação adicional: garantir que quantity não seja negativo após reserva
                    if from_stock.reserved_quantity + quantity > from_stock.quantity:
                        messages.error(
                            request,
                            f'Erro: A quantidade solicitada ({quantity}) excederia o estoque total ({from_stock.quantity}) após considerar as reservas existentes ({from_stock.reserved_quantity}).'
                        )
                        return redirect('branches:create_transfer')
                        
                except BranchStock.DoesNotExist:
                    messages.error(request, 'Medicamento não encontrado na filial de origem')
                    return redirect('branches:create_transfer')

                # Verificar se já existe transferência pendente para evitar duplicidade
                existing_transfer = StockTransfer.objects.filter(
                    from_branch=from_branch,
                    to_branch=to_branch,
                    medication=medication,
                    status='pending'
                ).exists()
                
                if existing_transfer:
                    messages.warning(
                        request,
                        'Já existe uma transferência pendente para este medicamento entre estas filiais.'
                    )
                    return redirect('branches:create_transfer')

                # Criar transferência
                transfer = StockTransfer.objects.create(
                    from_branch=from_branch,
                    to_branch=to_branch,
                    medication=medication,
                    quantity=quantity,
                    reason=reason,
                    requested_by=request.user
                )

                # Reservar estoque na filial de origem (usando update() para operação atômica)
                BranchStock.objects.filter(pk=from_stock.pk).update(
                    reserved_quantity=F('reserved_quantity') + quantity
                )

            # Enviar notificação
            notification_manager = NotificationManager()
            notification_manager.send_transfer_notification(transfer)

            messages.success(request, 'Solicitação de transferência criada com sucesso!')
            return redirect('branches:transfer_detail', pk=transfer.pk)

        except ValueError:
            messages.error(request, 'Dados inválidos fornecidos')
        except Exception as e:
            messages.error(request, f'Erro ao criar transferência: {str(e)}')
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao criar transferência: {str(e)}', exc_info=True)

    # Dados para o formulário
    branches = Branch.objects.filter(is_active=True)
    medications = Medication.objects.filter(is_active=True)

    context = {
        'branches': branches,
        'medications': medications
    }

    return render(request, 'branches/transfer_form.html', context)


@login_required
def transfer_detail(request, pk):
    """Detalhes de uma transferência"""
    transfer = get_object_or_404(StockTransfer, pk=pk)
    
    # Buscar estoques atualizados para sincronização
    try:
        from_stock = BranchStock.objects.get(
            branch=transfer.from_branch,
            medication=transfer.medication
        )
        to_stock = BranchStock.objects.filter(
            branch=transfer.to_branch,
            medication=transfer.medication
        ).first()
    except BranchStock.DoesNotExist:
        from_stock = None
        to_stock = None
    
    context = {
        'transfer': transfer,
        'from_stock': from_stock,
        'to_stock': to_stock
    }
    return render(request, 'branches/transfer_detail.html', context)


@login_required
def api_stock_sync(request, branch_pk, medication_pk):
    """API para sincronizar estoque no frontend"""
    try:
        stock = BranchStock.objects.get(
            branch_id=branch_pk,
            medication_id=medication_pk
        )
        return JsonResponse({
            'success': True,
            'quantity': stock.quantity,
            'reserved_quantity': stock.reserved_quantity,
            'available_quantity': stock.available_quantity,
            'last_updated': stock.last_updated.isoformat()
        })
    except BranchStock.DoesNotExist:
        return JsonResponse({
            'success': False,
            'available_quantity': 0,
            'error': 'Estoque não encontrado'
        })


@login_required
def api_get_available_stock(request):
    """API para buscar estoque disponível de um medicamento em uma filial"""
    branch_id = request.GET.get('branch_id')
    medication_id = request.GET.get('medication_id')
    
    if not branch_id or not medication_id:
        return JsonResponse({
            'success': False,
            'available_quantity': 0,
            'error': 'Parâmetros branch_id e medication_id são obrigatórios'
        }, status=400)
    
    try:
        stock = BranchStock.objects.get(
            branch_id=branch_id,
            medication_id=medication_id
        )
        return JsonResponse({
            'success': True,
            'quantity': stock.quantity,
            'reserved_quantity': stock.reserved_quantity,
            'available_quantity': stock.available_quantity,
            'is_low_stock': stock.is_low_stock
        })
    except BranchStock.DoesNotExist:
        return JsonResponse({
            'success': True,
            'quantity': 0,
            'reserved_quantity': 0,
            'available_quantity': 0,
            'is_low_stock': False
        })


@login_required
def api_branch_stats(request, branch_pk):
    """API para buscar estatísticas atualizadas de uma filial"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    
    # Calcular diretamente do banco para garantir sincronização
    branch_stocks = BranchStock.objects.filter(branch=branch)
    total_medications = branch_stocks.values('medication').distinct().count()
    total_stock_quantity = branch_stocks.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Calcular estoque baixo
    low_stock_count = 0
    for stock in branch_stocks.select_related('medication'):
        if stock.available_quantity <= stock.medication.minimum_stock:
            low_stock_count += 1
    
    return JsonResponse({
        'success': True,
        'total_medications': total_medications,
        'total_stock_quantity': total_stock_quantity,
        'low_stock_count': low_stock_count
    })


@admin_required
def approve_transfer(request, pk):
    """Aprovar e processar transferência com transação atômica e prevenção de duplicidade"""
    from django.db import transaction
    from django.db.models import F
    
    transfer = get_object_or_404(StockTransfer, pk=pk)
    
    if request.method == 'POST':
        # Verificar se já foi processada (prevenir duplicidade)
        if transfer.status != 'pending':
            messages.warning(request, f'Esta transferência já foi {transfer.get_status_display().lower()}.')
            return redirect('branches:transfer_detail', pk=pk)
        
        try:
            with transaction.atomic():
                # Usar select_for_update para lock e prevenir condições de corrida
                transfer = StockTransfer.objects.select_for_update().get(pk=pk)
                
                # Verificar novamente o status após lock
                if transfer.status != 'pending':
                    messages.warning(request, f'Esta transferência já foi processada.')
                    return redirect('branches:transfer_detail', pk=pk)
                
                # Obter estoques com lock
                from_stock = BranchStock.objects.select_for_update().get(
                    branch=transfer.from_branch,
                    medication=transfer.medication
                )
                
                # Verificar se há estoque suficiente (incluindo reservado)
                if from_stock.quantity < transfer.quantity:
                    messages.error(
                        request,
                        f'Estoque insuficiente na filial de origem. Disponível: {from_stock.quantity} unidades'
                    )
                    return redirect('branches:transfer_detail', pk=pk)
                
                if from_stock.reserved_quantity < transfer.quantity:
                    messages.error(
                        request,
                        f'Quantidade reservada insuficiente. Reservado: {from_stock.reserved_quantity} unidades'
                    )
                    return redirect('branches:transfer_detail', pk=pk)
                
                # Obter ou criar estoque de destino (com lock se existir)
                to_stock, created = BranchStock.objects.get_or_create(
                    branch=transfer.to_branch,
                    medication=transfer.medication,
                    defaults={'quantity': 0, 'reserved_quantity': 0}
                )
                
                # Se não foi criado, fazer lock
                if not created:
                    to_stock = BranchStock.objects.select_for_update().get(
                        branch=transfer.to_branch,
                        medication=transfer.medication
                    )
                
                # Processar transferência usando update() para operações atômicas
                BranchStock.objects.filter(pk=from_stock.pk).update(
                    quantity=F('quantity') - transfer.quantity,
                    reserved_quantity=F('reserved_quantity') - transfer.quantity
                )
                
                BranchStock.objects.filter(pk=to_stock.pk).update(
                    quantity=F('quantity') + transfer.quantity
                )
                
                # Atualizar status da transferência
                transfer.status = 'completed'
                transfer.approved_by = request.user
                transfer.completed_at = timezone.now()
                transfer.save(update_fields=['status', 'approved_by', 'completed_at'])
            
            messages.success(request, 'Transferência aprovada e processada com sucesso!')
            
        except BranchStock.DoesNotExist:
            messages.error(request, 'Estoque não encontrado na filial de origem.')
        except Exception as e:
            messages.error(request, f'Erro ao processar transferência: {str(e)}')
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao processar transferência {pk}: {str(e)}', exc_info=True)
    
    return redirect('branches:transfer_detail', pk=pk)


@login_required
def branch_dashboard(request):
    """Dashboard geral de filiais"""
    from django.http import HttpResponse
    
    branches = Branch.objects.filter(is_active=True)
    
    # Estatísticas gerais
    total_branches = branches.count()
    total_medications = BranchStock.objects.values('medication').distinct().count()
    
    # Filiais com estoque baixo
    branches_with_alerts = []
    for branch in branches:
        low_stock_count = branch.low_stock_count
        if low_stock_count > 0:
            branches_with_alerts.append({
                'branch': branch,
                'low_stock_count': low_stock_count
            })
    
    # Transferências pendentes
    pending_transfers = StockTransfer.objects.filter(status='pending').count()
    
    context = {
        'branches': branches,
        'total_branches': total_branches,
        'total_medications': total_medications,
        'branches_with_alerts': branches_with_alerts,
        'pending_transfers': pending_transfers
    }
    
    response = render(request, 'branches/dashboard.html', context)
    response['Content-Type'] = 'text/html; charset=utf-8'
    return response
