from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Branch, BranchStock, StockTransfer, BranchMedicationBatch
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
    """Detalhes de uma filial específica"""
    branch = get_object_or_404(Branch, pk=pk)
    
    # Estatísticas da filial
    branch_stocks = BranchStock.objects.filter(branch=branch).select_related('medication')
    
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
        'total_medications': branch.total_medications,
        'total_stock': branch.total_stock_quantity,
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
    
    # Query base com prefetch dos lotes
    stocks = BranchStock.objects.filter(branch=branch).select_related(
        'medication', 'medication__category'
    ).prefetch_related('batches')
    
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


@farmaceutico_required
def medication_batches_detail(request, branch_pk, stock_pk):
    """Detalhes dos lotes de um medicamento específico"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    stock = get_object_or_404(BranchStock, pk=stock_pk, branch=branch)
    
    # Buscar todos os lotes ativos ordenados por data de vencimento
    batches = BranchMedicationBatch.objects.filter(
        branch_stock=stock,
        is_active=True
    ).order_by('expiry_date')
    
    # Estatísticas dos lotes
    total_batches = batches.count()
    expired_count = sum(1 for batch in batches if batch.is_expired)
    near_expiry_count = sum(1 for batch in batches if batch.is_near_expiry)
    normal_count = total_batches - expired_count - near_expiry_count
    
    context = {
        'branch': branch,
        'stock': stock,
        'batches': batches,
        'total_batches': total_batches,
        'expired_count': expired_count,
        'near_expiry_count': near_expiry_count,
        'normal_count': normal_count,
    }
    
    return render(request, 'branches/medication_batches_detail.html', context)


@farmaceutico_required
def branch_expiry_dashboard(request, branch_pk):
    """Dashboard de vencimentos da filial"""
    branch = get_object_or_404(Branch, pk=branch_pk)
    
    # Buscar todos os stocks com seus lotes
    stocks = BranchStock.objects.filter(branch=branch).select_related(
        'medication', 'medication__category'
    ).prefetch_related('batches')
    
    # Calcular estatísticas gerais
    total_medications = stocks.count()
    expired_medications = sum(1 for stock in stocks if stock.expiry_status == 'expired')
    near_expiry_medications = sum(1 for stock in stocks if stock.expiry_status == 'near_expiry')
    
    # Buscar lotes vencidos e próximos ao vencimento
    all_batches = BranchMedicationBatch.objects.filter(
        branch_stock__branch=branch,
        is_active=True
    ).select_related('branch_stock__medication').order_by('expiry_date')
    
    expired_batches = [batch for batch in all_batches if batch.is_expired]
    near_expiry_batches = [batch for batch in all_batches if batch.is_near_expiry]
    
    context = {
        'branch': branch,
        'total_medications': total_medications,
        'expired_medications': expired_medications,
        'near_expiry_medications': near_expiry_medications,
        'expired_batches': expired_batches[:10],  # Primeiros 10
        'near_expiry_batches': near_expiry_batches[:10],  # Primeiros 10
        'total_expired_batches': len(expired_batches),
        'total_near_expiry_batches': len(near_expiry_batches),
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
    """Criar solicitação de transferência entre filiais"""
    if request.method == 'POST':
        try:
            from_branch_id = request.POST.get('from_branch')
            to_branch_id = request.POST.get('to_branch')
            medication_id = request.POST.get('medication')
            quantity = int(request.POST.get('quantity'))
            reason = request.POST.get('reason', '')
            
            # Validações
            if from_branch_id == to_branch_id:
                messages.error(request, 'Filial de origem deve ser diferente da filial de destino')
                return redirect('branches:create_transfer')
            
            from_branch = get_object_or_404(Branch, pk=from_branch_id)
            to_branch = get_object_or_404(Branch, pk=to_branch_id)
            medication = get_object_or_404(Medication, pk=medication_id)
            
            # Verificar se há estoque suficiente na filial de origem
            try:
                from_stock = BranchStock.objects.get(branch=from_branch, medication=medication)
                if from_stock.available_quantity < quantity:
                    messages.error(
                        request,
                        f'Estoque insuficiente. Disponível: {from_stock.available_quantity} unidades'
                    )
                    return redirect('branches:create_transfer')
            except BranchStock.DoesNotExist:
                messages.error(request, 'Medicamento não encontrado na filial de origem')
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
            
            # Reservar estoque na filial de origem
            from_stock.reserved_quantity += quantity
            from_stock.save()
            
            # Enviar notificação
            notification_manager = NotificationManager()
            notification_manager.send_transfer_notification(transfer)
            
            messages.success(request, 'Solicitação de transferência criada com sucesso!')
            return redirect('branches:transfer_detail', pk=transfer.pk)
            
        except ValueError:
            messages.error(request, 'Dados inválidos fornecidos')
        except Exception as e:
            messages.error(request, f'Erro ao criar transferência: {str(e)}')
    
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
    context = {'transfer': transfer}
    return render(request, 'branches/transfer_detail.html', context)


@admin_required
def approve_transfer(request, pk):
    """Aprovar e processar transferência"""
    transfer = get_object_or_404(StockTransfer, pk=pk)
    
    if request.method == 'POST' and transfer.status == 'pending':
        try:
            # Obter estoques
            from_stock = BranchStock.objects.get(
                branch=transfer.from_branch,
                medication=transfer.medication
            )
            to_stock, created = BranchStock.objects.get_or_create(
                branch=transfer.to_branch,
                medication=transfer.medication,
                defaults={'quantity': 0}
            )
            
            # Processar transferência
            from_stock.quantity -= transfer.quantity
            from_stock.reserved_quantity -= transfer.quantity
            from_stock.save()
            
            to_stock.quantity += transfer.quantity
            to_stock.save()
            
            # Atualizar status da transferência
            transfer.status = 'completed'
            transfer.approved_by = request.user
            transfer.completed_at = timezone.now()
            transfer.save()
            
            messages.success(request, 'Transferência aprovada e processada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar transferência: {str(e)}')
    
    return redirect('branches:transfer_detail', pk=pk)


@login_required
def branch_dashboard(request):
    """Dashboard geral de filiais"""
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
    
    return render(request, 'branches/dashboard.html', context)
