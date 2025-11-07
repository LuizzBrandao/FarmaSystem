from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('generate/', views.report_generate, name='report_generate'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/download/', views.report_download, name='report_download'),
    
    # Relatórios específicos - Nova implementação robusta
    path('stock/pdf/', views.stock_report_pdf, name='stock_report_pdf'),
    path('movements/pdf/', views.movements_report_pdf, name='movements_report_pdf'),
    path('expiration/pdf/', views.expiration_report_pdf, name='expiration_report_pdf'),
    
    # URLs de compatibilidade (redirecionam para novas implementações)
    path('stock/', views.stock_report, name='stock_report'),
    path('movements/', views.movement_report, name='movement_report'),
    path('expiry/', views.expiry_report, name='expiry_report'),
    
    # API endpoints
    path('api/pdf-status/', views.pdf_status_check, name='pdf_status_check'),
]
