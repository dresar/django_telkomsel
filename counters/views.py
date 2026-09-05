# TelkomselCounterApp/counters/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import messages framework
from django.http import Http404 # Import Http404
from django.urls import reverse # Import reverse untuk mendapatkan URL berdasarkan nama
from .models import Counter # Import Model Counter
from .forms import CounterRegistrationForm # Import Form Pendaftaran

# Create your views here.

@login_required # Pastikan user sudah login untuk mengakses view ini
def dashboard_view(request):
    """
    View untuk menampilkan halaman dashboard Counter.
    """
    # Mendapatkan objek Counter yang terkait dengan user yang sedang login
    try:
        counter = request.user.counter # Mengakses objek Counter melalui relasi OneToOneField
    except Counter.DoesNotExist:
        # Jika user login tapi belum punya objek Counter terkait
        # (misal: admin login, atau user baru yang baru daftar tapi Counter belum dibuat/terkait)

        # Cek apakah user ini punya is_staff=True (admin/petugas)
        if request.user.is_staff:
             # Jika staff/admin, arahkan ke halaman lain atau tampilkan pesan
             messages.warning(request, 'Anda login sebagai staf/admin tanpa data counter terkait.')
             # Contoh: arahkan ke panel admin
             return redirect(reverse('admin:index')) # Menggunakan reverse untuk URL admin

        # Jika user biasa (bukan staff) dan belum punya data Counter
        # Arahkan ke halaman pendaftaran agar melengkapi data
        messages.info(request, 'Silakan lengkapi data counter Anda untuk mengakses dashboard.')
        return redirect('counters:register_counter')


    # Jika user login dan punya objek Counter terkait, ambil data lain
    stock_items = counter.stock_items.all()
    topup_requests = counter.topup_requests.order_by('-tanggal_request')[:5]

    context = {
        'counter_data': counter,
        'stock_items': stock_items,
        'topup_requests': topup_requests,
        # Anda bisa tambahkan data lain di sini
    }

    # Render template dashboard.html (sudah di-namespaced di counters/templates/counters/)
    return render(request, 'counters/dashboard.html', context)


# View untuk pendaftaran counter
def register_counter(request):
    """
    View untuk menampilkan dan memproses form pendaftaran Counter.
    """
    # Jika user sudah login, cek apakah dia sudah punya data Counter
    if request.user.is_authenticated:
        if not request.user.is_staff: # Jika user login dan BUKAN admin/staff
             # Cek apakah user ini sudah punya data Counter
             if Counter.objects.filter(user=request.user).exists():
                 # Jika sudah punya data Counter, arahkan ke dashboard
                 messages.info(request, 'Anda sudah terdaftar sebagai Counter. Silakan akses dashboard Anda.')
                 return redirect('counters:dashboard')
             # Jika user login (bukan staff) tapi belum punya data Counter, biarkan lanjutkan pendaftaran
        else: # Jika user login dan adalah admin/staff
            # Admin/staff tidak perlu mendaftar via form ini, arahkan saja ke admin panel
            messages.warning(request, 'Anda login sebagai staf/admin. Gunakan panel admin untuk mengelola counter.')
            return redirect(reverse('admin:index'))


    if request.method == 'POST':
        # Tangani request POST & file uploads
        form = CounterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save() # Panggil method save di form (membuat User & Counter)
            # Setelah pendaftaran sukses
            messages.success(request, f'Akun "{user.username}" berhasil dibuat. Data counter Anda perlu diverifikasi oleh admin sebelum bisa login. Silakan coba login setelah ada konfirmasi.')
            # Arahkan user ke halaman login
            return redirect('login') # 'login' adalah nama URL login bawaan Django
        else:
             # Jika form tidak valid, error akan otomatis muncul di form saat dirender
             pass # Lanjut ke render form dengan error
    else: # Jika request GET
        form = CounterRegistrationForm() # Buat form kosong

    # Render template pendaftaran (sudah di-namespaced di counters/templates/counters/)
    return render(request, 'counters/register.html', {'form': form})