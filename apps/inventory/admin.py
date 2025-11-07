from django.contrib import admin
from .models import Category, Medication, Stock, StockMovement, Alert


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'supplier', 'price', 'minimum_stock', 'is_active']
    list_filter = ['category', 'supplier', 'is_active', 'requires_prescription']
    search_fields = ['name', 'barcode', 'active_principle']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['medication', 'quantity', 'expiry_date', 'batch_number', 'entry_date']
    list_filter = ['expiry_date', 'entry_date', 'is_active']
    search_fields = ['medication__name', 'batch_number']
    ordering = ['-entry_date']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['medication', 'movement_type', 'quantity', 'user', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['medication__name', 'reason']
    ordering = ['-created_at']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'medication', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved', 'created_at']
    search_fields = ['title', 'message']
    ordering = ['-created_at']