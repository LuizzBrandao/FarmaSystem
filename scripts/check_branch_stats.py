# -*- coding: utf-8 -*-
"""
Script para verificar e sincronizar estatísticas de filiais com o banco de dados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
django.setup()

from apps.branches.models import Branch, BranchStock
from django.db.models import Sum, Count

def check_branch_stats():
    """Verifica estatísticas de todas as filiais"""
    print("=" * 60)
    print("VERIFICANDO ESTATÍSTICAS DAS FILIAIS")
    print("=" * 60)
    
    branches = Branch.objects.filter(is_active=True)
    
    for branch in branches:
        # Calcular valores diretamente do banco
        total_stocks = branch.branch_stocks.count()
        total_medications = branch.branch_stocks.values('medication').distinct().count()
        total_quantity = branch.branch_stocks.aggregate(total=Sum('quantity'))['total'] or 0
        
        # Usar propriedades do modelo
        prop_medications = branch.total_medications
        prop_quantity = branch.total_stock_quantity
        prop_low_stock = branch.low_stock_count
        
        print(f"\nFilial: {branch.name} ({branch.code})")
        print(f"  Total de registros BranchStock: {total_stocks}")
        print(f"  Total de medicamentos únicos (direto): {total_medications}")
        print(f"  Total de medicamentos únicos (propriedade): {prop_medications}")
        print(f"  Total de unidades (direto): {total_quantity}")
        print(f"  Total de unidades (propriedade): {prop_quantity}")
        print(f"  Estoque baixo: {prop_low_stock}")
        
        # Verificar se há discrepâncias
        if total_medications != prop_medications:
            print(f"  ⚠️  DISCREPÂNCIA: Medicamentos - Direto: {total_medications}, Propriedade: {prop_medications}")
        if total_quantity != prop_quantity:
            print(f"  ⚠️  DISCREPÂNCIA: Unidades - Direto: {total_quantity}, Propriedade: {prop_quantity}")
        
        # Listar estoques
        print(f"\n  Detalhes dos estoques:")
        for stock in branch.branch_stocks.select_related('medication')[:10]:
            print(f"    - {stock.medication.name}: {stock.quantity} unidades (reservado: {stock.reserved_quantity})")
        if branch.branch_stocks.count() > 10:
            print(f"    ... e mais {branch.branch_stocks.count() - 10} medicamentos")
    
    print("\n" + "=" * 60)
    print("Verificação concluída!")
    print("=" * 60)

if __name__ == '__main__':
    check_branch_stats()


