from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Medicamentos
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/create/', views.medication_create, name='medication_create'),
    path('medications/<int:pk>/', views.medication_detail, name='medication_detail'),
    path('medications/<int:pk>/edit/', views.medication_edit, name='medication_edit'),
    path('medications/<int:pk>/delete/', views.medication_delete, name='medication_delete'),
    
    # Estoque
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/entry/', views.stock_entry, name='stock_entry'),
    path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('stock/movement/', views.stock_movement, name='stock_movement'),
    
    # Movimentações
    path('movements/', views.movement_list, name='movement_list'),
    path('movements/create/', views.movement_create, name='movement_create'),
    
    # Categorias
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:pk>/resolve/', views.alert_resolve, name='alert_resolve'),
]
