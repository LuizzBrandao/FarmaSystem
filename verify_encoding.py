# -*- coding: utf-8 -*-
"""
Script para verificar se todos os dados estão com encoding correto
Execute: python verify_encoding.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
django.setup()

from apps.branches.models import Branch
from apps.suppliers.models import Supplier
from apps.inventory.models import Category, Medication

print("Verificando encoding dos dados no banco...")
print("=" * 60)

# Verificar Filiais
print("\nFILIAIS:")
branches = Branch.objects.all()
for branch in branches:
    try:
        # Tentar codificar como UTF-8
        branch.name.encode('utf-8')
        branch.address.encode('utf-8')
        status = "OK"
    except:
        status = "ERRO"
    print(f"  [{branch.code}] {status} - {branch.name[:50]}")

# Verificar Fornecedores
print("\nFORNECEDORES:")
suppliers = Supplier.objects.all()[:10]  # Limitar a 10
for supplier in suppliers:
    try:
        supplier.name.encode('utf-8')
        status = "OK"
    except:
        status = "ERRO"
    print(f"  {status} - {supplier.name[:50]}")

# Verificar Categorias
print("\nCATEGORIAS:")
categories = Category.objects.all()
for cat in categories:
    try:
        cat.name.encode('utf-8')
        status = "OK"
    except:
        status = "ERRO"
    print(f"  {status} - {cat.name}")

print("\n" + "=" * 60)
print("Verificacao concluida!")

