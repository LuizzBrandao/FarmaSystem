from django.contrib import admin
from .models import Branch, BranchStock, StockTransfer, BranchMedicationBatch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager', 'email_notifications', 'whatsapp_notifications', 'is_active']
    list_filter = ['is_active', 'email_notifications', 'whatsapp_notifications', 'created_at']
    search_fields = ['name', 'code', 'email', 'manager__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'code', 'address', 'phone', 'email', 'manager', 'is_active')
        }),
        ('Configurações de Notificação', {
            'fields': ('email_notifications', 'whatsapp_notifications', 'whatsapp_number')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(BranchStock)
class BranchStockAdmin(admin.ModelAdmin):
    list_display = ['medication', 'branch', 'quantity', 'reserved_quantity', 'available_quantity', 'is_low_stock', 'last_updated']
    list_filter = ['branch', 'medication__category', 'last_updated']
    search_fields = ['medication__name', 'branch__name']
    readonly_fields = ['last_updated']
    
    def available_quantity(self, obj):
        return obj.available_quantity
    available_quantity.short_description = 'Disponível'
    
    def is_low_stock(self, obj):
        return '⚠️' if obj.is_low_stock else '✅'
    is_low_stock.short_description = 'Status'


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['medication', 'from_branch', 'to_branch', 'quantity', 'status', 'requested_by', 'requested_at']
    list_filter = ['status', 'from_branch', 'to_branch', 'requested_at']
    search_fields = ['medication__name', 'from_branch__name', 'to_branch__name', 'requested_by__username']
    readonly_fields = ['requested_at', 'completed_at']
    
    fieldsets = (
        ('Transferência', {
            'fields': ('from_branch', 'to_branch', 'medication', 'quantity', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'requested_by', 'approved_by')
        }),
        ('Datas', {
            'fields': ('requested_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )


@admin.register(BranchMedicationBatch)
class BranchMedicationBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'get_medication_name', 'get_branch_name', 'quantity', 'expiry_date', 'expiry_status_display', 'is_active']
    list_filter = ['is_active', 'expiry_date', 'branch_stock__branch', 'branch_stock__medication__category']
    search_fields = ['batch_number', 'branch_stock__medication__name', 'branch_stock__branch__name']
    readonly_fields = ['expiry_status_display', 'days_until_expiry', 'created_at', 'updated_at']
    date_hierarchy = 'expiry_date'
    
    fieldsets = (
        ('Informações do Lote', {
            'fields': ('branch_stock', 'batch_number', 'quantity', 'is_active')
        }),
        ('Datas', {
            'fields': ('manufacturing_date', 'expiry_date', 'expiry_status_display', 'days_until_expiry')
        }),
        ('Informações Comerciais', {
            'fields': ('purchase_price', 'supplier_reference'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_medication_name(self, obj):
        return obj.branch_stock.medication.name
    get_medication_name.short_description = 'Medicamento'
    get_medication_name.admin_order_field = 'branch_stock__medication__name'
    
    def get_branch_name(self, obj):
        return obj.branch_stock.branch.name
    get_branch_name.short_description = 'Filial'
    get_branch_name.admin_order_field = 'branch_stock__branch__name'
