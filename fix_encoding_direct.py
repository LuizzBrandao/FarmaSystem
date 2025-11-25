"""
Script para corrigir encoding dos dados de filiais no banco de dados
Execute: python manage.py shell
Depois execute: exec(open('fix_encoding_direct.py').read())
"""
import os
import sys
import django

# Forçar encoding UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
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
        needs_update = False
        
        # Verificar e atualizar nome
        if branch.name != correct_data['name']:
            branch.name = correct_data['name']
            needs_update = True
            print(f"  [{code}] Atualizando nome: {correct_data['name']}")
        
        # Verificar e atualizar endereço
        if branch.address != correct_data['address']:
            branch.address = correct_data['address']
            needs_update = True
            print(f"  [{code}] Atualizando endereço: {correct_data['address']}")
        
        if needs_update:
            # Garantir que os dados sejam salvos como UTF-8
            branch.name = correct_data['name'].encode('utf-8').decode('utf-8')
            branch.address = correct_data['address'].encode('utf-8').decode('utf-8')
            branch.save()
            updated_count += 1
            print(f"  [{code}] ✓ Dados atualizados com sucesso")
        else:
            print(f"  [{code}] ✓ Dados já estão corretos")
            
    except Branch.DoesNotExist:
        print(f"  [{code}] ⚠ Filial não encontrada")
    except Exception as e:
        print(f"  [{code}] ✗ Erro: {str(e)}")

print(f"\nConcluído! {updated_count} filiais atualizadas.")

