# -*- coding: utf-8 -*-
"""
Script para identificar e corrigir duplicidades em BranchStock
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
django.setup()

from apps.branches.models import BranchStock
from django.db.models import Count
from django.db import transaction

def find_duplicates():
    """Encontra registros duplicados de BranchStock"""
    print("=" * 60)
    print("VERIFICANDO DUPLICIDADES EM BRANCHSTOCK")
    print("=" * 60)
    
    # Encontrar duplicidades baseadas em (branch, medication)
    duplicates = BranchStock.objects.values(
        'branch', 'medication'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if not duplicates.exists():
        print("\n✅ Nenhuma duplicidade encontrada!")
        return []
    
    print(f"\n⚠️  Encontradas {duplicates.count()} combinações duplicadas:")
    print("-" * 60)
    
    duplicate_list = []
    for dup in duplicates:
        branch_id = dup['branch']
        medication_id = dup['medication']
        count = dup['count']
        
        stocks = BranchStock.objects.filter(
            branch_id=branch_id,
            medication_id=medication_id
        ).order_by('id')
        
        print(f"\nFilial ID: {branch_id}, Medicamento ID: {medication_id}")
        print(f"  Total de registros: {count}")
        
        total_quantity = 0
        total_reserved = 0
        
        for stock in stocks:
            print(f"    ID: {stock.id} | Qtd: {stock.quantity} | Reservado: {stock.reserved_quantity}")
            total_quantity += stock.quantity
            total_reserved += stock.reserved_quantity
        
        duplicate_list.append({
            'branch_id': branch_id,
            'medication_id': medication_id,
            'stocks': list(stocks),
            'total_quantity': total_quantity,
            'total_reserved': total_reserved
        })
    
    return duplicate_list


def fix_duplicates(dry_run=True):
    """Corrige duplicidades mantendo apenas o primeiro registro e somando quantidades"""
    duplicates = find_duplicates()
    
    if not duplicates:
        return
    
    print("\n" + "=" * 60)
    if dry_run:
        print("MODO DRY-RUN (simulação - nenhuma alteração será feita)")
    else:
        print("CORRIGINDO DUPLICIDADES")
    print("=" * 60)
    
    fixed_count = 0
    
    with transaction.atomic():
        for dup_info in duplicates:
            stocks = dup_info['stocks']
            if len(stocks) <= 1:
                continue
            
            # Manter o primeiro registro (mais antigo)
            keep_stock = stocks[0]
            
            # Somar todas as quantidades
            total_quantity = dup_info['total_quantity']
            total_reserved = dup_info['total_reserved']
            
            print(f"\nCorrigindo: Filial {dup_info['branch_id']}, Medicamento {dup_info['medication_id']}")
            print(f"  Mantendo registro ID: {keep_stock.id}")
            print(f"  Quantidade total: {total_quantity}")
            print(f"  Reservado total: {total_reserved}")
            print(f"  Removendo {len(stocks) - 1} registro(s) duplicado(s)")
            
            if not dry_run:
                # Atualizar o registro mantido
                keep_stock.quantity = total_quantity
                keep_stock.reserved_quantity = total_reserved
                keep_stock.save()
                
                # Remover duplicados
                for stock in stocks[1:]:
                    print(f"    Removendo ID: {stock.id}")
                    stock.delete()
                
                fixed_count += 1
    
    if dry_run:
        print("\n" + "=" * 60)
        print("DRY-RUN concluído. Execute com --fix para aplicar as correções.")
    else:
        print("\n" + "=" * 60)
        print(f"✅ Correção concluída! {fixed_count} duplicidade(s) corrigida(s).")
    
    print("=" * 60)


if __name__ == '__main__':
    import sys
    
    if '--fix' in sys.argv:
        print("\n⚠️  ATENÇÃO: Isso irá modificar o banco de dados!")
        response = input("Deseja continuar? (sim/não): ")
        if response.lower() in ['sim', 's', 'yes', 'y']:
            fix_duplicates(dry_run=False)
        else:
            print("Operação cancelada.")
    else:
        fix_duplicates(dry_run=True)


