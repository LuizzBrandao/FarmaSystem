from django.contrib import admin
from .models import MedicationBatch, BatchLocation


@admin.register(MedicationBatch)
class MedicationBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'get_medication_name', 'expiry_date', 'expiry_status_display', 'initial_quantity', 'get_total_in_system', 'is_active']
    list_filter = ['is_active', 'expiry_date', 'medication__category', 'created_at']
    search_fields = ['batch_number', 'medication__name', 'supplier_reference']
    readonly_fields = ['expiry_status_display', 'days_until_expiry', 'get_total_in_system', 'get_available_in_system', 'created_at', 'updated_at']
    date_hierarchy = 'expiry_date'
    
    fieldsets = (
        ('Informações do Lote', {
            'fields': ('batch_number', 'medication', 'initial_quantity', 'is_active')
        }),
        ('Datas', {
            'fields': ('manufacturing_date', 'expiry_date', 'expiry_status_display', 'days_until_expiry')
        }),
        ('Quantidades no Sistema', {
            'fields': ('get_total_in_system', 'get_available_in_system'),
            'classes': ('collapse',)
        }),
        ('Informações Comerciais', {
            'fields': ('purchase_price', 'supplier_reference'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_medication_name(self, obj):
        return obj.medication.name
    get_medication_name.short_description = 'Medicamento'
    get_medication_name.admin_order_field = 'medication__name'
    
    def get_total_in_system(self, obj):
        total = sum(loc.quantity for loc in obj.locations.filter(is_active=True))
        return f"{total} unidades"
    get_total_in_system.short_description = 'Total no Sistema'
    
    def get_available_in_system(self, obj):
        available = sum(loc.available_quantity for loc in obj.locations.filter(is_active=True))
        return f"{available} unidades"
    get_available_in_system.short_description = 'Disponível no Sistema'
    
    def expiry_status_display(self, obj):
        status = obj.expiry_status
        color_map = {
            'normal': 'green',
            'near_expiry': 'orange',
            'expired': 'red'
        }
        color = color_map.get(status, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{obj.expiry_status_display}</span>'
    expiry_status_display.short_description = 'Status Vencimento'
    expiry_status_display.allow_tags = True


@admin.register(BatchLocation)
class BatchLocationAdmin(admin.ModelAdmin):
    list_display = ['get_batch_number', 'get_medication_name', 'location_type', 'get_location_name', 'quantity', 'reserved_quantity', 'available_quantity', 'is_active']
    list_filter = ['location_type', 'is_active', 'branch', 'batch__expiry_date']
    search_fields = ['batch__batch_number', 'batch__medication__name', 'branch__name']
    readonly_fields = ['available_quantity', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Localização', {
            'fields': ('batch', 'location_type', 'branch')
        }),
        ('Quantidades', {
            'fields': ('quantity', 'reserved_quantity', 'available_quantity')
        }),
        ('Controles', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_batch_number(self, obj):
        return obj.batch.batch_number
    get_batch_number.short_description = 'Número do Lote'
    get_batch_number.admin_order_field = 'batch__batch_number'
    
    def get_medication_name(self, obj):
        return obj.batch.medication.name
    get_medication_name.short_description = 'Medicamento'
    get_medication_name.admin_order_field = 'batch__medication__name'
    
    def get_location_name(self, obj):
        return obj.location_name
    get_location_name.short_description = 'Localização'
    
    def available_quantity(self, obj):
        return obj.available_quantity
    available_quantity.short_description = 'Disponível'
