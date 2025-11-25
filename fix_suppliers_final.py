# -*- coding: utf-8 -*-
"""
Script final para corrigir encoding dos fornecedores
Execute: python fix_suppliers_final.py
"""
import sqlite3
import os

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

print("Corrigindo fornecedores no SQLite...")

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA encoding = 'UTF-8'")
cursor = conn.cursor()

# Dados corretos
correct_name = 'Fornecedor Exemplo Marília'
correct_address = 'Marília - SP'

try:
    # Atualizar todos os fornecedores que contenham "Fornecedor Exemplo"
    cursor.execute(
        "UPDATE suppliers_supplier SET name = ?, address = ? WHERE name LIKE '%Fornecedor Exemplo%'",
        (correct_name, correct_address)
    )
    
    rows_affected = cursor.rowcount
    conn.commit()
    
    print(f"[OK] {rows_affected} fornecedor(es) atualizado(s)")
    print(f"     Nome: {correct_name}")
    print(f"     Endereco: {correct_address}")
    
except Exception as e:
    print(f"[ERRO] {str(e)}")
finally:
    conn.close()

print("\nCorrecao concluida!")


