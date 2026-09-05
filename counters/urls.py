# TelkomselCounterApp/counters/urls.py

from django.urls import path # Tidak perlu include jika tidak ada sub-url lagi
from . import views
from django.views.generic.base import RedirectView # Untuk redirect root URL

app_name = 'counters' # Namespace untuk aplikasi ini

urlpatterns = [
    # Redirect dari root URL aplikasi ('') ke halaman pendaftaran
    path('', RedirectView.as_view(pattern_name='counters:register_counter', permanent=False), name='index'),

    # URL untuk halaman dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # URL untuk halaman pendaftaran
    path('register/', views.register_counter, name='register_counter'),

    # URL lain akan ditambahkan di sini (misal: stok, topup)
    # path('stock/', views.stock_list_view, name='stock_list'),
    # path('topup/', views.topup_request_view, name='topup_request'),
]