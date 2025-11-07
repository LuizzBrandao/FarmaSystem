from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard principal (já existente)
    path('', views.dashboard, name='dashboard'),
    
    # ESTOQUE PRINCIPAL - Rota consolidada
    path('estoque/', views.complete_stock_view, name='estoque'),
    
    # NOVAS URLs UNIFICADAS para controle de lotes
    
    # Vista unificada de todos os lotes
    path('unified-stock/', views.unified_stock_view, name='unified_stock'),
    
    # Detalhes de um lote específico
    path('batch/<str:batch_number>/', views.batch_detail_view, name='batch_detail'),
    
    # Vista por localização (compatibilidade com URLs existentes)
    path('stock/general/', views.location_stock_view, {'location_type': 'general'}, name='general_stock'),
    path('stock/branch/<int:location_id>/', views.location_stock_view, {'location_type': 'branch'}, name='branch_stock_unified'),
    
    # Relatórios de consistência
    path('consistency-report/', views.batch_consistency_report, name='consistency_report'),
    
    # URLs para botões do dashboard
    path('complete-stock/', views.complete_stock_view, name='complete_stock'),
    path('system-integrity/', views.system_integrity_view, name='system_integrity'),
    
    # APIs para integração
    path('api/batch/<str:batch_number>/locations/', views.api_batch_locations, name='api_batch_locations'),
    path('api/medication/<int:medication_id>/batches/', views.api_medication_batches, name='api_medication_batches'),
]