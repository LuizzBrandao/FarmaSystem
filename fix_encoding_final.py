# -*- coding: utf-8 -*-
"""
Script para corrigir encoding dos dados de filiais no banco de dados
Execute: python fix_encoding_final.py
"""
import os
import sys
import django

# Forçar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
django.setup()

from apps.branches.models import Branch

# Dados corretos das filiais com encoding UTF-8
branches_correct_data = {
    'MAR001': {
        'name': 'Filial Centro - Drogasil Sampaio Vidal',
        'address': 'Av. Sampaio Vidal, 589 - Centro, Marília - SP, 17500-020',
    },
    'MAR002': {
        'name': 'Filial Centro - Drogaria São Paulo Sampaio Vidal',
        'address': 'Av. Sampaio Vidal, 506 - Centro, Marília - SP, 17500-021',
    },
    'MAR003': {
        'name': 'Filial Palmital - Droga Raia República',
        'address': 'Av. República, 3281 - Qd 44, Palmital, Marília - SP, 17510-402',
    },
    'MAR004': {
        'name': 'Filial Centro - Pague Menos Coronel Galdino',
        'address': 'Rua Coronel Galdino de Almeida, 142 - Centro, Marília - SP, 17500-100',
    },
    'MAR005': {
        'name': 'Filial Alto Cafezal - Drogaria São Paulo Rio Branco',
        'address': 'Av. Rio Branco, 800 - Alto Cafezal, Marília - SP',
    },
}

print("Corrigindo encoding dos dados de filiais...")
updated_count = 0

for code, correct_data in branches_correct_data.items():
    try:
        branch = Branch.objects.get(code=code)
        
        # Atualizar diretamente com os dados corretos
        branch.name = correct_data['name']
        branch.address = correct_data['address']
        branch.save(update_fields=['name', 'address'])
        
        updated_count += 1
        print(f"  [{code}] Atualizado: {correct_data['name']}")
            
    except Branch.DoesNotExist:
        print(f"  [{code}] Filial nao encontrada")
    except Exception as e:
        print(f"  [{code}] Erro: {str(e)}")

print(f"\nConcluido! {updated_count} filiais atualizadas.")


