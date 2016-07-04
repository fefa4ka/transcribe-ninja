# -*- coding: utf-8 -*-

from site import admin_site

from yandex_money.models import Payment

from django.contrib.admin import ModelAdmin


class PaymentAdmin(ModelAdmin):
    list_display_links = ('customer_number',)
    list_display = (
        'customer_number',
        'payment_type',
        'order_number',
        'order_amount',
        'shop_amount',
        'shop_currency',
        'invoice_id',
        'status',
        'pub_date',
        'user',
        'cps_phone',
    )
    list_filter = (
        'pub_date',
        'status',
    )
    search_fields = (
        'customer_number',
        'cps_email',
        'cps_phone',
        'scid',
        'shop_id',
        'invoice_id',
        'order_number',
    )

    def has_add_permission(self, obj):
        return False


admin_site.register(Payment, PaymentAdmin)
