from django.urls import path
from . import views
from . import api_views as api

app_name = 'core'

urlpatterns = [
    # Dashboard principal (já existente)
    path('', views.dashboard, name='dashboard'),

    # Redirecionamento do antigo Estoque para lista de filiais
    path('estoque/', views.estoque_redirect, name='estoque'),

    # Rotas antigas dependentes de LOTE comentadas
    # path('unified-stock/', views.unified_stock_view, name='unified_stock'),
    # path('batch/<str:batch_number>/', views.batch_detail_view, name='batch_detail'),
    # path('stock/general/', views.location_stock_view, {'location_type': 'general'}, name='general_stock'),
    # path('stock/branch/<int:location_id>/', views.location_stock_view, {'location_type': 'branch'}, name='branch_stock_unified'),
    # path('consistency-report/', views.batch_consistency_report, name='consistency_report'),
    
    # Integridade do sistema
    path('system-integrity/', views.system_integrity_view, name='system_integrity'),
    
    # APIs antigas de lote removidas
    # path('api/batch/<str:batch_number>/locations/', views.api_batch_locations, name='api_batch_locations'),
    # path('api/medication/<int:medication_id>/batches/', views.api_medication_batches, name='api_medication_batches'),
]