# -*- coding: utf-8 -*-
"""
Script para corrigir encoding diretamente no SQLite
Execute: python fix_sqlite_encoding.py
"""
import sqlite3
import os

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Dados corretos
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

print("Conectando ao banco de dados SQLite...")
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA encoding = 'UTF-8'")
cursor = conn.cursor()

print("Atualizando dados das filiais...")
updated = 0

for code, data in branches_data.items():
    try:
        # Atualizar nome e endereço diretamente no SQLite
        cursor.execute(
            "UPDATE branches_branch SET name = ?, address = ? WHERE code = ?",
            (data['name'], data['address'], code)
        )
        if cursor.rowcount > 0:
            updated += 1
            print(f"  [{code}] Atualizado: {data['name']}")
        else:
            print(f"  [{code}] Nao encontrado")
    except Exception as e:
        print(f"  [{code}] Erro: {str(e)}")

conn.commit()
conn.close()

print(f"\nConcluido! {updated} filiais atualizadas no banco de dados.")


