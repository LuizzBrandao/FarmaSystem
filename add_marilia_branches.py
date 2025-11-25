# -*- coding: utf-8 -*-
"""
Script para adicionar 5 filiais de exemplo em Marília-SP e alguns medicamentos padrão
Execute: python manage.py shell < add_marilia_branches.py
"""

from django.contrib.auth.models import User
from apps.branches.models import Branch, BranchStock
from apps.inventory.models import Medication, Category
from apps.suppliers.models import Supplier
from decimal import Decimal


def get_or_create_default_supplier():
    supplier, _ = Supplier.objects.get_or_create(
        name="Fornecedor Exemplo Marília",
        defaults={
            'email': 'contato@exemplo.com',
            'phone': '+5514999999999',
            'address': 'Marília - SP',
            'contact_person': 'Equipe',
            'cnpj': '00.000.000/0001-00',
            'is_active': True,
        }
    )
    return supplier


def get_or_create_default_category():
    category, _ = Category.objects.get_or_create(
        name="Geral",
        defaults={'description': 'Categoria padrão'}
    )
    return category


def ensure_medications():
    names = [
        'Paracetamol 500mg', 'Dipirona 500mg',
        'Ibuprofeno 600mg', 'Loratadina 10mg',
        'Omeprazol 20mg'
    ]
    meds = list(Medication.objects.filter(name__in=names))
    missing = set(names) - set(m.name for m in meds)
    if missing:
        supplier = Supplier.objects.first() or get_or_create_default_supplier()
        category = Category.objects.first() or get_or_create_default_category()
        for name in missing:
            meta = {
                'Paracetamol 500mg': {'price': '8.50', 'active_principle': 'Paracetamol', 'dosage': '500mg', 'pharmaceutical_form': 'Comprimido'},
                'Dipirona 500mg': {'price': '6.90', 'active_principle': 'Dipirona Sódica', 'dosage': '500mg', 'pharmaceutical_form': 'Comprimido'},
                'Ibuprofeno 600mg': {'price': '11.50', 'active_principle': 'Ibuprofeno', 'dosage': '600mg', 'pharmaceutical_form': 'Comprimido'},
                'Loratadina 10mg': {'price': '12.30', 'active_principle': 'Loratadina', 'dosage': '10mg', 'pharmaceutical_form': 'Comprimido'},
                'Omeprazol 20mg': {'price': '16.70', 'active_principle': 'Omeprazol', 'dosage': '20mg', 'pharmaceutical_form': 'Cápsula'},
            }[name]
            med = Medication.objects.create(
                name=name,
                description=f'Medicamento de exemplo ({name})',
                category=category,
                supplier=supplier,
                barcode=None,
                price=Decimal(meta['price']),
                minimum_stock=30,
                active_principle=meta['active_principle'],
                dosage=meta['dosage'],
                pharmaceutical_form=meta['pharmaceutical_form'],
            )
            meds.append(med)
    return meds


def create_branches():
    admin = User.objects.filter(username='admin').first()
    branches_data = [
        {
            'name': 'Filial Centro - Drogasil Sampaio Vidal',
            'code': 'MAR001',
            'address': 'Av. Sampaio Vidal, 589 - Centro, Marília - SP, 17500-020',
            'phone': '+551434338061',
            'email': 'mar001@exemplo.com',
            'manager': admin,
            'whatsapp_number': '+551434338061',
        },
        {
            'name': 'Filial Centro - Drogaria São Paulo Sampaio Vidal',
            'code': 'MAR002',
            'address': 'Av. Sampaio Vidal, 506 - Centro, Marília - SP, 17500-021',
            'phone': '+551434225275',
            'email': 'mar002@exemplo.com',
            'manager': admin,
            'whatsapp_number': '+551434225275',
        },
        {
            'name': 'Filial Palmital - Droga Raia República',
            'code': 'MAR003',
            'address': 'Av. República, 3281 - Qd 44, Palmital, Marília - SP, 17510-402',
            'phone': '+5514996283000',
            'email': 'mar003@exemplo.com',
            'manager': admin,
            'whatsapp_number': '+5514996283000',
        },
        {
            'name': 'Filial Centro - Pague Menos Coronel Galdino',
            'code': 'MAR004',
            'address': 'Rua Coronel Galdino de Almeida, 142 - Centro, Marília - SP, 17500-100',
            'phone': '+551434321872',
            'email': 'mar004@exemplo.com',
            'manager': admin,
            'whatsapp_number': '+551434321872',
        },
        {
            'name': 'Filial Alto Cafezal - Drogaria São Paulo Rio Branco',
            'code': 'MAR005',
            'address': 'Av. Rio Branco, 800 - Alto Cafezal, Marília - SP',
            'phone': '+5514999999998',
            'email': 'mar005@exemplo.com',
            'manager': admin,
            'whatsapp_number': '+5514999999998',
        },
    ]
    created = []
    for data in branches_data:
        branch, created_flag = Branch.objects.get_or_create(
            code=data['code'],
            defaults={
                'name': data['name'],
                'address': data['address'],
                'phone': data['phone'],
                'email': data['email'],
                'manager': data['manager'],
                'whatsapp_number': data['whatsapp_number'],
                'email_notifications': True,
                'whatsapp_notifications': False,
                'is_active': True,
            }
        )
        if not created_flag:
            branch.name = data['name']
            branch.address = data['address']
            branch.phone = data['phone']
            branch.email = data['email']
            branch.manager = data['manager']
            branch.whatsapp_number = data['whatsapp_number']
            branch.is_active = True
            branch.save()
        created.append(branch)
    return created


def seed_branch_stocks(branches, medications):
    quantities = [120, 80, 150, 60, 100]
    for branch in branches:
        for i, med in enumerate(medications):
            qty = quantities[i % len(quantities)]
            bs, _ = BranchStock.objects.get_or_create(
                branch=branch,
                medication=med,
                defaults={'quantity': qty, 'reserved_quantity': qty // 10}
            )
            bs.quantity = qty
            bs.reserved_quantity = qty // 10
            bs.save()


print("Criando/garantindo medicamentos padrão...")
meds = ensure_medications()
print(f"Medicamentos disponíveis: {', '.join(m.name for m in meds)}")

print("Criando filiais de exemplo em Marília-SP...")
branches = create_branches()
print(f"Filiais criadas/atualizadas: {len(branches)}")

print("Criando estoques por filial (BranchStock)...")
seed_branch_stocks(branches, meds)
print("Concluído com sucesso!")

# Resumo
from apps.branches.models import BranchStock
from django.db.models import Sum
total_stocks = BranchStock.objects.aggregate(total=Sum('quantity'))['total'] or 0
print(f"Total de itens em estoque (todas filiais): {total_stocks}")
print(f"Total de filiais: {len(branches)}; Total de medicamentos por filial (média): {sum(b.total_medications for b in branches)/len(branches):.1f}")