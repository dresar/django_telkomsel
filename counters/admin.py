# TelkomselCounterApp/counters/admin.py

from django.contrib import admin
# Import semua model yang ingin dikelola di admin
from .models import Counter, Product, CounterStock, TopUpRequest, Transaction

# Register your models here.
admin.site.register(Counter)
admin.site.register(Product)
admin.site.register(CounterStock)
admin.site.register(TopUpRequest)
admin.site.register(Transaction)

# Nanti, untuk tampilan yang lebih baik, Anda bisa custom dengan AdminModel
# class CounterAdmin(admin.ModelAdmin):
#     list_display = ('nama_counter', 'user', 'status_verifikasi', 'saldo', 'tanggal_bergabung')
#     list_filter = ('status_verifikasi',)
#     search_fields = ('nama_counter', 'user__username', 'nama_pemilik')
# admin.site.register(Counter, CounterAdmin)