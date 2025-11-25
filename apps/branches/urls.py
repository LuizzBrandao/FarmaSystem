from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    # Dashboard geral
    path('', views.branch_dashboard, name='dashboard'),
    
    # Filiais
    path('list/', views.branch_list, name='branch_list'),
    path('<int:pk>/', views.branch_detail, name='branch_detail'),
    
    # Estoque por filial
    path('<int:branch_pk>/stock/', views.branch_stock_view, name='branch_stock'),
    path('<int:branch_pk>/stock/<int:medication_pk>/update/', views.update_branch_stock, name='update_stock'),
    # URL medication_batches_detail foi removida - funcionalidade de lotes removida
    path('<int:branch_pk>/expiry-dashboard/', views.branch_expiry_dashboard, name='expiry_dashboard'),
    
    # Transferências
    path('transfers/create/', views.create_transfer, name='create_transfer'),
    path('transfers/<int:pk>/', views.transfer_detail, name='transfer_detail'),
    path('transfers/<int:pk>/approve/', views.approve_transfer, name='approve_transfer'),
    
    # API para sincronização
    path('api/stock/<int:branch_pk>/<int:medication_pk>/sync/', views.api_stock_sync, name='api_stock_sync'),
    path('api/stock/available/', views.api_get_available_stock, name='api_get_available_stock'),
    path('api/<int:branch_pk>/stats/', views.api_branch_stats, name='api_branch_stats'),
]
