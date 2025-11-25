# -*- coding: utf-8 -*-
"""
Script para corrigir encoding dos fornecedores no banco de dados
Execute: python fix_suppliers_encoding.py
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

from apps.suppliers.models import Supplier

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

print("Corrigindo encoding dos fornecedores...")
print("=" * 60)

# Dados corretos dos fornecedores
suppliers_data = [
    {
        'old_name': 'Fornecedor Exemplo Mar??lia',
        'name': 'Fornecedor Exemplo Marília',
        'address': 'Marília - SP',
    },
    {
        'old_name': 'Fornecedor Exemplo Marília',
        'name': 'Fornecedor Exemplo Marília',
        'address': 'Marília - SP',
    },
]

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA encoding = 'UTF-8'")
cursor = conn.cursor()

updated = 0

# Primeiro, vamos buscar todos os fornecedores e corrigir
for supplier_data in suppliers_data:
    try:
        # Buscar fornecedores que contenham o nome antigo
        cursor.execute(
            "SELECT id, name, address FROM suppliers_supplier WHERE name LIKE ? OR name LIKE ?",
            (f"%{supplier_data['old_name']}%", "%Fornecedor Exemplo%")
        )
        rows = cursor.fetchall()
        
        for row_id, old_name, old_address in rows:
            # Corrigir nome e endereço
            new_name = supplier_data['name']
            new_address = supplier_data['address']
            
            # Se o endereço antigo contém "Mar??lia", corrigir
            if 'Mar??lia' in old_address or 'Marília' not in old_address:
                new_address = supplier_data['address']
            
            cursor.execute(
                "UPDATE suppliers_supplier SET name = ?, address = ? WHERE id = ?",
                (new_name, new_address, row_id)
            )
            if cursor.rowcount > 0:
                updated += 1
                print(f"  [OK] ID {row_id}: {old_name} -> {new_name}")
    except Exception as e:
        print(f"  [ERRO] Erro: {str(e)}")

conn.commit()
conn.close()

# Também corrigir via ORM para garantir
print("\nCorrigindo via ORM...")
try:
    suppliers = Supplier.objects.filter(name__icontains='Fornecedor Exemplo')
    for supplier in suppliers:
        needs_update = False
        if 'Mar??lia' in supplier.name or 'Marília' not in supplier.name:
            supplier.name = 'Fornecedor Exemplo Marília'
            needs_update = True
        if 'Mar??lia' in supplier.address or ('Marília' not in supplier.address and 'Mar' in supplier.address):
            supplier.address = 'Marília - SP'
            needs_update = True
        if needs_update:
            supplier.save(update_fields=['name', 'address'])
            print(f"  [OK] ORM: {supplier.name}")
            updated += 1
except Exception as e:
    print(f"  [ERRO] Erro ORM: {str(e)}")

print(f"\n{updated} fornecedor(es) atualizado(s) com sucesso!")

