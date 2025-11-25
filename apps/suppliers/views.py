# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier


@login_required
def supplier_list(request):
    """Lista de fornecedores"""
    from django.http import HttpResponse
    
    suppliers = Supplier.objects.filter(is_active=True)
    context = {'suppliers': suppliers}
    response = render(request, 'suppliers/supplier_list.html', context)
    response['Content-Type'] = 'text/html; charset=utf-8'
    return response


@login_required
def supplier_create(request):
    """Criar novo fornecedor"""
    if request.method == 'POST':
        # Lógica para criar fornecedor
        messages.success(request, 'Fornecedor criado com sucesso!')
        return redirect('suppliers:supplier_list')
    
    return render(request, 'suppliers/supplier_form.html')


@login_required
def supplier_detail(request, pk):
    """Detalhes do fornecedor"""
    from django.http import HttpResponse
    
    supplier = get_object_or_404(Supplier, pk=pk)
    context = {'supplier': supplier}
    response = render(request, 'suppliers/supplier_detail.html', context)
    response['Content-Type'] = 'text/html; charset=utf-8'
    return response


@login_required
def supplier_edit(request, pk):
    """Editar fornecedor"""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        # Lógica para editar fornecedor
        messages.success(request, 'Fornecedor atualizado com sucesso!')
        return redirect('suppliers:supplier_detail', pk=pk)
    
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_form.html', context)


@login_required
def supplier_delete(request, pk):
    """Deletar fornecedor"""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.is_active = False
        supplier.save()
        messages.success(request, 'Fornecedor removido com sucesso!')
        return redirect('suppliers:supplier_list')
    
    context = {'supplier': supplier}
    return render(request, 'suppliers/supplier_confirm_delete.html', context)