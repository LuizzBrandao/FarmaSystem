# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados de teste
Execute: python manage.py shell < populate_data.py
"""

from apps.suppliers.models import Supplier
from apps.inventory.models import Category, Medication, Stock, Alert
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

# Criar fornecedores
print("Criando fornecedores...")
supplier1 = Supplier.objects.create(
    name="Farmacêutica Brasil LTDA",
    email="contato@farmbrasil.com.br",
    phone="+5511999999999",
    address="Rua das Indústrias, 123 - São Paulo, SP",
    contact_person="João Silva",
    cnpj="12.345.678/0001-90"
)

supplier2 = Supplier.objects.create(
    name="MedSupply Distribuidora",
    email="vendas@medsupply.com.br",
    phone="+5511888888888",
    address="Av. Paulista, 456 - São Paulo, SP",
    contact_person="Maria Santos",
    cnpj="98.765.432/0001-10"
)

supplier3 = Supplier.objects.create(
    name="Laboratório Nacional",
    email="comercial@labnacional.com.br",
    phone="+5511777777777",
    address="Rua da Saúde, 789 - Rio de Janeiro, RJ",
    contact_person="Carlos Oliveira",
    cnpj="11.222.333/0001-44"
)

# Criar categorias
print("Criando categorias...")
cat_analgesicos = Category.objects.create(
    name="Analgésicos",
    description="Medicamentos para alívio da dor"
)

cat_antibioticos = Category.objects.create(
    name="Antibióticos",
    description="Medicamentos para combate a infecções bacterianas"
)

cat_antialergicos = Category.objects.create(
    name="Antialérgicos",
    description="Medicamentos para tratamento de alergias"
)

cat_vitaminas = Category.objects.create(
    name="Vitaminas e Suplementos",
    description="Vitaminas e suplementos alimentares"
)

cat_dermato = Category.objects.create(
    name="Dermatológicos",
    description="Medicamentos para tratamento da pele"
)

# Criar medicamentos
print("Criando medicamentos...")
medications_data = [
    {
        'name': 'Paracetamol 500mg',
        'description': 'Analgésico e antitérmico',
        'category': cat_analgesicos,
        'supplier': supplier1,
        'barcode': '7891234567890',
        'price': Decimal('8.50'),
        'minimum_stock': 50,
        'active_principle': 'Paracetamol',
        'dosage': '500mg',
        'pharmaceutical_form': 'Comprimido'
    },
    {
        'name': 'Amoxicilina 500mg',
        'description': 'Antibiótico de amplo espectro',
        'category': cat_antibioticos,
        'supplier': supplier2,
        'barcode': '7891234567891',
        'price': Decimal('15.80'),
        'minimum_stock': 30,
        'active_principle': 'Amoxicilina',
        'dosage': '500mg',
        'pharmaceutical_form': 'Cápsula',
        'requires_prescription': True
    },
    {
        'name': 'Dipirona 500mg',
        'description': 'Analgésico e antitérmico',
        'category': cat_analgesicos,
        'supplier': supplier1,
        'barcode': '7891234567892',
        'price': Decimal('6.90'),
        'minimum_stock': 40,
        'active_principle': 'Dipirona Sódica',
        'dosage': '500mg',
        'pharmaceutical_form': 'Comprimido'
    },
    {
        'name': 'Loratadina 10mg',
        'description': 'Antialérgico de longa duração',
        'category': cat_antialergicos,
        'supplier': supplier3,
        'barcode': '7891234567893',
        'price': Decimal('12.30'),
        'minimum_stock': 25,
        'active_principle': 'Loratadina',
        'dosage': '10mg',
        'pharmaceutical_form': 'Comprimido'
    },
    {
        'name': 'Vitamina C 1000mg',
        'description': 'Suplemento vitamínico',
        'category': cat_vitaminas,
        'supplier': supplier2,
        'barcode': '7891234567894',
        'price': Decimal('18.90'),
        'minimum_stock': 20,
        'active_principle': 'Ácido Ascórbico',
        'dosage': '1000mg',
        'pharmaceutical_form': 'Comprimido efervescente'
    },
    {
        'name': 'Ibuprofeno 600mg',
        'description': 'Anti-inflamatório e analgésico',
        'category': cat_analgesicos,
        'supplier': supplier1,
        'barcode': '7891234567895',
        'price': Decimal('11.50'),
        'minimum_stock': 35,
        'active_principle': 'Ibuprofeno',
        'dosage': '600mg',
        'pharmaceutical_form': 'Comprimido'
    },
    {
        'name': 'Cetoconazol 2% Creme',
        'description': 'Antifúngico para uso tópico',
        'category': cat_dermato,
        'supplier': supplier3,
        'barcode': '7891234567896',
        'price': Decimal('9.80'),
        'minimum_stock': 15,
        'active_principle': 'Cetoconazol',
        'dosage': '2%',
        'pharmaceutical_form': 'Creme'
    },
    {
        'name': 'Omeprazol 20mg',
        'description': 'Inibidor da bomba de prótons',
        'category': cat_analgesicos,  # Pode criar uma categoria específica
        'supplier': supplier2,
        'barcode': '7891234567897',
        'price': Decimal('16.70'),
        'minimum_stock': 30,
        'active_principle': 'Omeprazol',
        'dosage': '20mg',
        'pharmaceutical_form': 'Cápsula'
    }
]

medications = []
for med_data in medications_data:
    medication = Medication.objects.create(**med_data)
    medications.append(medication)

# Criar estoque
print("Criando estoque...")
for i, medication in enumerate(medications):
    # Criar alguns lotes para cada medicamento
    for j in range(2, 4):  # 2-3 lotes por medicamento
        quantity = 100 + (i * 20) + (j * 10)
        
        # Algumas com vencimento próximo, outras normais
        if i % 3 == 0:  # Alguns próximos ao vencimento
            expiry_days = 25
        elif i % 4 == 0:  # Alguns vencidos
            expiry_days = -5
        else:  # Maioria com vencimento normal
            expiry_days = 180 + (i * 30)
            
        expiry_date = timezone.now().date() + timedelta(days=expiry_days)
        
        Stock.objects.create(
            medication=medication,
            quantity=quantity,
            expiry_date=expiry_date,
            batch_number=f'LOTE{i+1:03d}{j:02d}',
            purchase_price=medication.price * Decimal('0.7')  # 70% do preço de venda
        )

# Criar alguns alertas
print("Criando alertas...")
admin_user = User.objects.get(username='admin')

# Alerta de estoque baixo
Alert.objects.create(
    medication=medications[0],
    alert_type='estoque_baixo',
    title='Estoque Baixo - Paracetamol',
    message='O medicamento Paracetamol 500mg está com estoque abaixo do mínimo recomendado.'
)

# Alerta de vencimento próximo
Alert.objects.create(
    medication=medications[1],
    alert_type='vencimento_proximo',
    title='Vencimento Próximo - Amoxicilina',
    message='Lotes de Amoxicilina 500mg vencem em menos de 30 dias.'
)

# Alerta de medicamento vencido
Alert.objects.create(
    medication=medications[2],
    alert_type='vencido',
    title='Medicamento Vencido - Dipirona',
    message='Lotes de Dipirona 500mg estão vencidos e devem ser retirados do estoque.'
)

print("Dados de teste criados com sucesso!")
print(f"- {Supplier.objects.count()} fornecedores")
print(f"- {Category.objects.count()} categorias") 
print(f"- {Medication.objects.count()} medicamentos")
print(f"- {Stock.objects.count()} lotes em estoque")
print(f"- {Alert.objects.count()} alertas")
