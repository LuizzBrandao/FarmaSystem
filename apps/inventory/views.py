from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Medication, Category, Stock, StockMovement, Alert
from apps.suppliers.models import Supplier
from apps.authentication.decorators import role_required, admin_required, farmaceutico_required


@login_required
def medication_list(request):
    """Lista de medicamentos"""
    medications = Medication.objects.filter(is_active=True).select_related('category', 'supplier')
    context = {'medications': medications}
    return render(request, 'inventory/medication_list.html', context)


@farmaceutico_required
def medication_create(request):
    """Criar novo medicamento"""
    if request.method == 'POST':
        try:
            medication = Medication.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                category_id=request.POST.get('category'),
                supplier_id=request.POST.get('supplier'),
                price=request.POST.get('price', 0),
                minimum_stock=request.POST.get('minimum_stock', 10),
                barcode=request.POST.get('barcode', ''),
                active_principle=request.POST.get('active_principle', ''),
                dosage=request.POST.get('dosage', ''),
                pharmaceutical_form=request.POST.get('pharmaceutical_form', ''),
                requires_prescription=bool(request.POST.get('requires_prescription'))
            )
            messages.success(request, 'Medicamento criado com sucesso!')
            return redirect('inventory:medication_detail', pk=medication.pk)
        except Exception as e:
            messages.error(request, f'Erro ao criar medicamento: {str(e)}')
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.filter(is_active=True)
    context = {'categories': categories, 'suppliers': suppliers}
    return render(request, 'inventory/medication_form.html', context)


@login_required
def medication_detail(request, pk):
    """Detalhes do medicamento"""
    medication = get_object_or_404(Medication, pk=pk)
    context = {'medication': medication}
    return render(request, 'inventory/medication_detail.html', context)


@farmaceutico_required
def medication_edit(request, pk):
    """Editar medicamento"""
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        try:
            # Atualizar dados do medicamento
            medication.name = request.POST.get('name', medication.name)
            medication.description = request.POST.get('description', medication.description)
            
            # Validar e atualizar categoria
            category_id = request.POST.get('category')
            if category_id:
                medication.category_id = category_id
            
            # Validar e atualizar fornecedor
            supplier_id = request.POST.get('supplier')
            if supplier_id:
                medication.supplier_id = supplier_id
            
            # Atualizar preço com validação
            price = request.POST.get('price')
            if price:
                try:
                    medication.price = float(price)
                except ValueError:
                    messages.error(request, 'Preço inválido.')
                    return redirect('inventory:medication_edit', pk=pk)
            
            # Atualizar estoque mínimo
            minimum_stock = request.POST.get('minimum_stock')
            if minimum_stock:
                try:
                    medication.minimum_stock = int(minimum_stock)
                except ValueError:
                    messages.error(request, 'Estoque mínimo deve ser um número inteiro.')
                    return redirect('inventory:medication_edit', pk=pk)
            
            # Atualizar outros campos
            medication.barcode = request.POST.get('barcode', medication.barcode)
            medication.active_principle = request.POST.get('active_principle', medication.active_principle)
            medication.dosage = request.POST.get('dosage', medication.dosage)
            medication.pharmaceutical_form = request.POST.get('pharmaceutical_form', medication.pharmaceutical_form)
            medication.requires_prescription = bool(request.POST.get('requires_prescription'))
            
            # Salvar no banco de dados
            medication.save()
            
            messages.success(request, 'Medicamento atualizado com sucesso!')
            return redirect('inventory:medication_detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar medicamento: {str(e)}')
            return redirect('inventory:medication_edit', pk=pk)
    
    categories = Category.objects.all()
    suppliers = Supplier.objects.filter(is_active=True)
    context = {'medication': medication, 'categories': categories, 'suppliers': suppliers}
    return render(request, 'inventory/medication_form.html', context)


@admin_required
def medication_delete(request, pk):
    """Deletar medicamento"""
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        medication.is_active = False
        medication.save()
        messages.success(request, 'Medicamento removido com sucesso!')
        return redirect('inventory:medication_list')
    
    context = {'medication': medication}
    return render(request, 'inventory/medication_confirm_delete.html', context)


@login_required
def stock_list(request):
    """Lista de estoque"""
    stock_items = Stock.objects.filter(is_active=True).select_related('medication')
    context = {'stock_items': stock_items}
    return render(request, 'inventory/stock_list.html', context)


@farmaceutico_required
def stock_entry(request):
    """Entrada de estoque"""
    if request.method == 'POST':
        try:
            # Criar nova entrada de estoque
            stock = Stock.objects.create(
                medication_id=request.POST.get('medication'),
                quantity=int(request.POST.get('quantity')),
                batch_number=request.POST.get('batch_number'),
                expiry_date=request.POST.get('expiry_date'),
                purchase_price=request.POST.get('purchase_price', 0),
                selling_price=request.POST.get('selling_price', 0),
                supplier_id=request.POST.get('supplier') if request.POST.get('supplier') else None
            )
            
            # Registrar movimentação
            StockMovement.objects.create(
                medication=stock.medication,
                movement_type='entrada',
                quantity=stock.quantity,
                reference_number=stock.batch_number,
                notes=f'Entrada de estoque - Lote {stock.batch_number}',
                user=request.user
            )
            
            messages.success(request, f'Entrada de estoque registrada com sucesso! Lote: {stock.batch_number}')
            return redirect('inventory:stock_detail', pk=stock.pk)
        except Exception as e:
            messages.error(request, f'Erro ao registrar entrada: {str(e)}')
    
    medications = Medication.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)
    context = {'medications': medications, 'suppliers': suppliers}
    return render(request, 'inventory/stock_entry_form.html', context)


@login_required
def stock_detail(request, pk):
    """Detalhes do estoque"""
    stock = get_object_or_404(Stock, pk=pk)
    context = {'stock': stock}
    return render(request, 'inventory/stock_detail.html', context)


@login_required
def movement_list(request):
    """Lista de movimentações"""
    movements = StockMovement.objects.all().select_related('medication', 'user').order_by('-created_at')
    context = {'movements': movements}
    return render(request, 'inventory/movement_list.html', context)


@login_required
def movement_create(request):
    """Criar movimentação"""
    if request.method == 'POST':
        # Lógica para criar movimentação
        messages.success(request, 'Movimentação registrada com sucesso!')
        return redirect('inventory:movement_list')
    
    medications = Medication.objects.filter(is_active=True)
    context = {'medications': medications}
    return render(request, 'inventory/movement_form.html', context)


@login_required
def category_list(request):
    """Lista de categorias"""
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'inventory/category_list.html', context)


@login_required
def category_create(request):
    """Criar categoria"""
    if request.method == 'POST':
        # Lógica para criar categoria
        messages.success(request, 'Categoria criada com sucesso!')
        return redirect('inventory:category_list')
    
    return render(request, 'inventory/category_form.html')


@login_required
def alert_list(request):
    """Lista de alertas"""
    alerts = Alert.objects.filter(is_resolved=False).order_by('-created_at')
    context = {'alerts': alerts}
    return render(request, 'inventory/alert_list.html', context)


@login_required
def alert_resolve(request, pk):
    """Resolver alerta"""
    alert = get_object_or_404(Alert, pk=pk)
    alert.is_resolved = True
    alert.resolved_by = request.user
    alert.save()
    
    messages.success(request, 'Alerta resolvido com sucesso!')
    return redirect('inventory:alert_list')


@login_required
@farmaceutico_required
def stock_movement(request):
    """Processar movimentação de estoque"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            stock_id = request.POST.get('stock_id')
            movement_type = request.POST.get('movement_type')
            quantity = int(request.POST.get('quantity'))
            movement_date = request.POST.get('movement_date')
            notes = request.POST.get('notes', '')
            
            # Validar dados
            if not all([stock_id, movement_type, quantity, movement_date]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('inventory:stock_list')
            
            # Obter o lote de estoque
            stock = get_object_or_404(Stock, pk=stock_id)
            
            # Validar quantidade disponível para saídas
            if movement_type in ['saida', 'ajuste_negativo', 'perda']:
                if quantity > stock.quantity:
                    messages.error(request, f'Quantidade insuficiente. Disponível: {stock.quantity} unidades.')
                    return redirect('inventory:stock_list')
            
            # Calcular nova quantidade
            if movement_type in ['saida', 'ajuste_negativo', 'perda']:
                new_quantity = stock.quantity - quantity
            elif movement_type in ['ajuste_positivo']:
                new_quantity = stock.quantity + quantity
            else:  # transferencia
                new_quantity = stock.quantity - quantity
            
            # Validar se não fica negativo
            if new_quantity < 0:
                messages.error(request, 'A movimentação resultaria em estoque negativo.')
                return redirect('inventory:stock_list')
            
            # Criar registro de movimentação
            from datetime import datetime
            movement_date_obj = datetime.strptime(movement_date, '%Y-%m-%d').date()
            
            movement = StockMovement.objects.create(
                medication=stock.medication,
                movement_type=movement_type,
                quantity=quantity,
                user=request.user,
                notes=notes,
                created_at=movement_date_obj
            )
            
            # Atualizar quantidade do lote
            stock.quantity = new_quantity
            stock.save()
            
            # Criar alerta se estoque ficou baixo
            if stock.medication.is_low_stock:
                Alert.objects.get_or_create(
                    medication=stock.medication,
                    alert_type='estoque_baixo',
                    defaults={
                        'title': f'Estoque baixo: {stock.medication.name}',
                        'message': f'Medicamento com apenas {stock.medication.current_stock} unidades em estoque.',
                        'priority': 'medium'
                    }
                )
            
            # Mensagem de sucesso
            movement_type_display = {
                'saida': 'Saída',
                'ajuste_positivo': 'Ajuste Positivo',
                'ajuste_negativo': 'Ajuste Negativo',
                'perda': 'Perda',
                'transferencia': 'Transferência'
            }.get(movement_type, movement_type)
            
            messages.success(
                request, 
                f'Movimentação registrada com sucesso! {movement_type_display} de {quantity} unidades de {stock.medication.name}.'
            )
            
        except ValueError as e:
            messages.error(request, 'Dados inválidos fornecidos.')
        except Exception as e:
            messages.error(request, f'Erro ao processar movimentação: {str(e)}')
    
    return redirect('inventory:stock_list')