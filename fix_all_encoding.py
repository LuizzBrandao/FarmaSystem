# -*- coding: utf-8 -*-
"""
Script completo para corrigir encoding de todos os dados no banco de dados
Execute: python fix_all_encoding.py
"""
import os
import sys
import django
import sqlite3

# Forçar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
django.setup()

from apps.branches.models import Branch
from apps.suppliers.models import Supplier
from apps.inventory.models import Category, Medication

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

print("=" * 60)
print("CORREÇÃO COMPLETA DE ENCODING - TODOS OS DADOS")
print("=" * 60)

# 1. CORRIGIR FILIAIS
print("\n[1] Corrigindo Filiais...")
branches_data = {
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

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA encoding = 'UTF-8'")
cursor = conn.cursor()

branches_updated = 0
for code, data in branches_data.items():
    try:
        cursor.execute(
            "UPDATE branches_branch SET name = ?, address = ? WHERE code = ?",
            (data['name'], data['address'], code)
        )
        if cursor.rowcount > 0:
            branches_updated += 1
            print(f"  [OK] [{code}] {data['name']}")
    except Exception as e:
        print(f"  [ERRO] [{code}] Erro: {str(e)}")

# 2. CORRIGIR FORNECEDORES
print("\n[2] Corrigindo Fornecedores...")
suppliers_data = [
    {
        'old_name': 'Fornecedor Exemplo Marília',
        'name': 'Fornecedor Exemplo Marília',
        'address': 'Marília - SP',
    },
    {
        'old_name': 'Farmacêutica Brasil LTDA',
        'name': 'Farmacêutica Brasil LTDA',
        'address': 'Rua das Indústrias, 123 - São Paulo, SP',
    },
    {
        'old_name': 'MedSupply Distribuidora',
        'name': 'MedSupply Distribuidora',
        'address': 'Av. Paulista, 456 - São Paulo, SP',
    },
    {
        'old_name': 'Laboratório Nacional',
        'name': 'Laboratório Nacional',
        'address': 'Rua da Saúde, 789 - Rio de Janeiro, RJ',
    },
]

suppliers_updated = 0
for supplier_data in suppliers_data:
    try:
        cursor.execute(
            "UPDATE suppliers_supplier SET name = ?, address = ? WHERE name LIKE ?",
            (supplier_data['name'], supplier_data['address'], f"%{supplier_data['old_name']}%")
        )
        if cursor.rowcount > 0:
            suppliers_updated += 1
            print(f"  [OK] {supplier_data['name']}")
    except Exception as e:
        print(f"  [ERRO] Erro ao atualizar fornecedor: {str(e)}")

# 3. CORRIGIR CATEGORIAS
print("\n[3] Corrigindo Categorias...")
categories_data = [
    {'old_name': 'Geral', 'name': 'Geral', 'description': 'Categoria padrão'},
    {'old_name': 'Analgésicos', 'name': 'Analgésicos', 'description': 'Medicamentos para alívio da dor'},
    {'old_name': 'Antibióticos', 'name': 'Antibióticos', 'description': 'Medicamentos para combate a infecções bacterianas'},
    {'old_name': 'Antialérgicos', 'name': 'Antialérgicos', 'description': 'Medicamentos para tratamento de alergias'},
    {'old_name': 'Vitaminas e Suplementos', 'name': 'Vitaminas e Suplementos', 'description': 'Vitaminas e suplementos alimentares'},
    {'old_name': 'Dermatológicos', 'name': 'Dermatológicos', 'description': 'Medicamentos para tratamento da pele'},
]

categories_updated = 0
for cat_data in categories_data:
    try:
        cursor.execute(
            "UPDATE inventory_category SET name = ?, description = ? WHERE name LIKE ?",
            (cat_data['name'], cat_data['description'], f"%{cat_data['old_name']}%")
        )
        if cursor.rowcount > 0:
            categories_updated += 1
            print(f"  [OK] {cat_data['name']}")
    except Exception as e:
        print(f"  [ERRO] Erro ao atualizar categoria: {str(e)}")

# 4. CORRIGIR MEDICAMENTOS COM CARACTERES ESPECIAIS
print("\n[4] Corrigindo Medicamentos...")
medications_data = [
    {
        'old_name': 'Dipirona Sódica',
        'active_principle': 'Dipirona Sódica',
        'pharmaceutical_form': 'Comprimido',
    },
]

medications_updated = 0
for med_data in medications_data:
    try:
        # Atualizar principio ativo
        cursor.execute(
            "UPDATE inventory_medication SET active_principle = ? WHERE active_principle LIKE ?",
            (med_data['active_principle'], f"%{med_data['old_name']}%")
        )
        if cursor.rowcount > 0:
            medications_updated += cursor.rowcount
            print(f"  [OK] {med_data['active_principle']} ({cursor.rowcount} registros)")
    except Exception as e:
        print(f"  [ERRO] Erro ao atualizar medicamento: {str(e)}")

# Commit todas as alterações
conn.commit()
conn.close()

# 5. VERIFICAR E CORRIGIR VIA ORM (para garantir)
print("\n[5] Verificando e corrigindo via ORM...")
orm_updated = 0

# Filiais
for code, data in branches_data.items():
    try:
        branch = Branch.objects.get(code=code)
        if branch.name != data['name'] or branch.address != data['address']:
            branch.name = data['name']
            branch.address = data['address']
            branch.save(update_fields=['name', 'address'])
            orm_updated += 1
    except Branch.DoesNotExist:
        pass
    except Exception as e:
        print(f"  [ERRO] Erro ao atualizar filial {code}: {str(e)}")

print("\n" + "=" * 60)
print("RESUMO DA CORREÇÃO")
print("=" * 60)
print(f"Filiais atualizadas: {branches_updated}")
print(f"Fornecedores atualizados: {suppliers_updated}")
print(f"Categorias atualizadas: {categories_updated}")
print(f"Medicamentos atualizados: {medications_updated}")
print(f"Registros corrigidos via ORM: {orm_updated}")
print(f"\nTotal de registros corrigidos: {branches_updated + suppliers_updated + categories_updated + medications_updated + orm_updated}")
print("\n[OK] Correcao concluida com sucesso!")

