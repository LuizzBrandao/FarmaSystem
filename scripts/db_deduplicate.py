import os
import sys
from collections import defaultdict
from typing import List, Tuple

# Garantir que o diretório raiz do projeto esteja no PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management.settings')
import django
django.setup()

from django.db import transaction
from django.db.models import Count, Sum, Min, Max

from apps.inventory.models import Medication, Stock, StockMovement, Alert, Category
from apps.suppliers.models import Supplier
from apps.branches.models import BranchStock, BranchMedicationBatch, StockTransfer
from apps.core.models import MedicationBatch, BatchLocation


def log(msg):
    print(msg)


def dedup_medications_by_barcode(commit: bool = False):
    log("\n[1] Verificando duplicidades de Medication por barcode...")
    dups = (
        Medication.objects
        .exclude(barcode__isnull=True)
        .exclude(barcode='')
        .values('barcode')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    total_groups = dups.count()
    log(f" - Grupos duplicados encontrados: {total_groups}")
    actions = []

    for group in dups:
        barcode = group['barcode']
        meds = list(Medication.objects.filter(barcode=barcode).order_by('id'))
        canonical = meds[0]
        others = meds[1:]
        log(f"   * barcode={barcode}: manter id={canonical.id}, mesclar {len(others)} duplicatas")
        actions.append((canonical, others))

    if not commit:
        log(" - Modo análise: nenhuma alteração aplicada")
        return actions

    with transaction.atomic():
        for canonical, others in actions:
            # Reatribuir FKs para Medication
            for dup in others:
                # Atualiza estoques da filial
                BranchStock.objects.filter(medication=dup).update(medication=canonical)
                # Movimentações de estoque
                StockMovement.objects.filter(medication=dup).update(medication=canonical)
                # Alertas
                Alert.objects.filter(medication=dup).update(medication=canonical)
                # Estoque geral
                Stock.objects.filter(medication=dup).update(medication=canonical)
                # Lotes unificados
                MedicationBatch.objects.filter(medication=dup).update(medication=canonical)
                # Transferências
                StockTransfer.objects.filter(medication=dup).update(medication=canonical)
                # Finalmente remover o duplicado
                dup.delete()
        log(" - Duplicatas de Medication resolvidas com sucesso")
    return actions


def dedup_suppliers_by_cnpj(commit: bool = False):
    log("\n[2] Verificando duplicidades de Supplier por CNPJ...")
    dups = (
        Supplier.objects
        .exclude(cnpj__isnull=True)
        .exclude(cnpj='')
        .values('cnpj')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    total_groups = dups.count()
    log(f" - Grupos duplicados encontrados: {total_groups}")
    actions = []

    for group in dups:
        cnpj = group['cnpj']
        sups = list(Supplier.objects.filter(cnpj=cnpj).order_by('id'))
        canonical = sups[0]
        others = sups[1:]
        log(f"   * cnpj={cnpj}: manter id={canonical.id}, mesclar {len(others)} duplicatas")
        actions.append((canonical, others))

    if not commit:
        log(" - Modo análise: nenhuma alteração aplicada")
        return actions

    with transaction.atomic():
        for canonical, others in actions:
            for dup in others:
                # Reatribuir medicamentos para fornecedor canônico
                Medication.objects.filter(supplier=dup).update(supplier=canonical)
                dup.delete()
        log(" - Duplicatas de Supplier resolvidas com sucesso")
    return actions


def dedup_stock_by_medication_batch(commit: bool = False):
    log("\n[3] Verificando duplicidades em Stock por (medication_id, batch_number)...")
    dups = (
        Stock.objects
        .values('medication_id', 'batch_number')
        .annotate(cnt=Count('id'), total_qty=Sum('quantity'))
        .filter(cnt__gt=1)
    )
    total_groups = dups.count()
    log(f" - Grupos duplicados encontrados: {total_groups}")
    actions = []

    for group in dups:
        med_id = group['medication_id']
        batch = group['batch_number']
        rows = list(Stock.objects.filter(medication_id=med_id, batch_number=batch).order_by('id'))
        canonical = rows[0]
        others = rows[1:]
        # Consolidar valores
        sum_qty = sum(r.quantity for r in rows)
        min_entry = min([r.entry_date for r in rows if r.entry_date]) if any(r.entry_date for r in rows) else None
        # Expiry: pegar a menor data (mais crítica)
        expiry_candidates = [r.expiry_date for r in rows if r.expiry_date]
        new_expiry = min(expiry_candidates) if expiry_candidates else canonical.expiry_date
        actions.append({
            'canonical_id': canonical.id,
            'medication_id': med_id,
            'batch_number': batch,
            'new_quantity': sum_qty,
            'new_expiry_date': new_expiry,
            'new_entry_date': min_entry,
            'to_delete': [r.id for r in others]
        })
        log(f"   * med={med_id} batch={batch}: manter id={canonical.id}, qty-> {sum_qty}, deletar {len(others)}")

    if not commit:
        log(" - Modo análise: nenhuma alteração aplicada")
        return actions

    with transaction.atomic():
        for act in actions:
            canonical = Stock.objects.get(id=act['canonical_id'])
            canonical.quantity = act['new_quantity']
            if act['new_expiry_date']:
                canonical.expiry_date = act['new_expiry_date']
            if act['new_entry_date']:
                canonical.entry_date = act['new_entry_date']
            canonical.save()
            # Remover duplicatas
            Stock.objects.filter(id__in=act['to_delete']).delete()
        log(" - Duplicatas de Stock resolvidas com sucesso")
    return actions


def dedup_branch_batches(commit: bool = False):
    log("\n[4] Verificando duplicidades em BranchMedicationBatch por (branch_stock_id, batch_number)...")
    dups = (
        BranchMedicationBatch.objects
        .values('branch_stock_id', 'batch_number')
        .annotate(cnt=Count('id'), total_qty=Sum('quantity'))
        .filter(cnt__gt=1)
    )
    total_groups = dups.count()
    log(f" - Grupos duplicados encontrados: {total_groups}")
    actions = []

    for group in dups:
        bs_id = group['branch_stock_id']
        batch = group['batch_number']
        rows = list(BranchMedicationBatch.objects.filter(branch_stock_id=bs_id, batch_number=batch).order_by('id'))
        canonical = rows[0]
        others = rows[1:]
        sum_qty = sum(r.quantity for r in rows)
        # expiry: menor data (mais próxima)
        expiry_candidates = [r.expiry_date for r in rows if r.expiry_date]
        new_expiry = min(expiry_candidates) if expiry_candidates else canonical.expiry_date
        # manuf: menor data mais antiga
        manuf_candidates = [r.manufacturing_date for r in rows if r.manufacturing_date]
        new_manuf = min(manuf_candidates) if manuf_candidates else canonical.manufacturing_date
        actions.append({
            'canonical_id': canonical.id,
            'new_quantity': sum_qty,
            'new_expiry_date': new_expiry,
            'new_manufacturing_date': new_manuf,
            'to_delete': [r.id for r in others]
        })
        log(f"   * branch_stock={bs_id} batch={batch}: manter id={canonical.id}, qty-> {sum_qty}, deletar {len(others)}")

    if not commit:
        log(" - Modo análise: nenhuma alteração aplicada")
        return actions

    with transaction.atomic():
        for act in actions:
            canonical = BranchMedicationBatch.objects.get(id=act['canonical_id'])
            canonical.quantity = act['new_quantity']
            if act['new_expiry_date']:
                canonical.expiry_date = act['new_expiry_date']
            if act['new_manufacturing_date']:
                canonical.manufacturing_date = act['new_manufacturing_date']
            canonical.save()
            BranchMedicationBatch.objects.filter(id__in=act['to_delete']).delete()
        log(" - Duplicatas de BranchMedicationBatch resolvidas com sucesso")
    return actions


def report_medicationbatch_duplicates():
    log("\n[5] Checando duplicidades em MedicationBatch (core) por batch_number...")
    dups = (
        MedicationBatch.objects
        .values('batch_number')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    total_groups = dups.count()
    log(f" - Grupos duplicados encontrados: {total_groups}")
    details = []
    for group in dups:
        batch = group['batch_number']
        rows = list(MedicationBatch.objects.filter(batch_number=batch).order_by('id'))
        meds = list(set(r.medication_id for r in rows))
        details.append({
            'batch_number': batch,
            'ids': [r.id for r in rows],
            'medication_ids': meds,
            'count': len(rows)
        })
        log(f"   * batch={batch}: ids={details[-1]['ids']}, meds={meds}")
    return details


def merge_medicationbatch_duplicates(commit: bool = False):
    """Consolida duplicidades de MedicationBatch somente quando todos registros referem o mesmo medication."""
    details = report_medicationbatch_duplicates()
    if not details:
        return []

    actions = []
    for info in details:
        if len(info['medication_ids']) > 1:
            log(f"   ! PULANDO batch={info['batch_number']} (medications conflitantes: {info['medication_ids']})")
            continue
        rows = list(MedicationBatch.objects.filter(id__in=info['ids']).order_by('id'))
        canonical = rows[0]
        others = rows[1:]
        # Decisões: initial_quantity -> soma? Escolher o máximo para evitar inflar.
        new_initial_qty = max([r.initial_quantity for r in rows if r.initial_quantity is not None] or [canonical.initial_quantity])
        # expiry -> menor (mais crítica)
        expiry_candidates = [r.expiry_date for r in rows if r.expiry_date]
        new_expiry = min(expiry_candidates) if expiry_candidates else canonical.expiry_date
        actions.append({
            'batch_number': info['batch_number'],
            'canonical_id': canonical.id,
            'new_initial_quantity': new_initial_qty,
            'new_expiry_date': new_expiry,
            'other_ids': [r.id for r in others]
        })
        log(f"   * batch={info['batch_number']}: manter id={canonical.id}, initial_qty->{new_initial_qty}, deletar {len(others)}")

    if not commit:
        log(" - Modo análise: nenhuma alteração aplicada em MedicationBatch")
        return actions

    with transaction.atomic():
        for act in actions:
            canonical = MedicationBatch.objects.get(id=act['canonical_id'])
            if act['new_initial_quantity'] is not None:
                canonical.initial_quantity = act['new_initial_quantity']
            if act['new_expiry_date']:
                canonical.expiry_date = act['new_expiry_date']
            canonical.save()
            # Reatribuir BatchLocation dos outros para o canônico, mesclando se necessário
            for other_id in act['other_ids']:
                for loc in BatchLocation.objects.filter(batch_id=other_id):
                    # Tenta encontrar localização equivalente no canônico
                    existing = BatchLocation.objects.filter(
                        batch_id=canonical.id,
                        location_type=loc.location_type,
                        branch_id=loc.branch_id
                    ).first()
                    if existing:
                        existing.quantity += loc.quantity
                        existing.reserved_quantity += loc.reserved_quantity
                        existing.save()
                        loc.delete()
                    else:
                        loc.batch_id = canonical.id
                        loc.save()
                # Remover o batch duplicado
                MedicationBatch.objects.filter(id=other_id).delete()
        log(" - Duplicatas de MedicationBatch consolidadas (sem conflitos)")
    return actions


if __name__ == '__main__':
    commit = '--commit' in sys.argv
    log("Iniciando análise de duplicidades (commit=%s)" % commit)
    dedup_medications_by_barcode(commit=commit)
    dedup_suppliers_by_cnpj(commit=commit)
    dedup_stock_by_medication_batch(commit=commit)
    dedup_branch_batches(commit=commit)
    report_medicationbatch_duplicates()
    # Tentar mesclar MedicationBatch sem conflito
    merge_medicationbatch_duplicates(commit=commit)
    log("\nConcluído.")