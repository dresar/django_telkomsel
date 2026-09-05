# TelkomselCounterApp/counters/models.py

from django.db import models
from django.contrib.auth import get_user_model # Lebih baik pakai get_user_model
# Jangan lupa import field types yang dipakai
from django.db.models import ImageField, DecimalField, ForeignKey, OneToOneField, CharField, TextField, DateTimeField, BooleanField, PositiveIntegerField, EmailField

User = get_user_model() # Dapatkan Model User aktif

# Pilihan untuk Status Verifikasi Counter
STATUS_VERIFIKASI_CHOICES = [
    ('Pending', 'Menunggu Verifikasi'),
    ('Verified', 'Terverifikasi'),
    ('Rejected', 'Ditolak'),
]

# Pilihan untuk Jenis Transaksi
JENIS_TRANSAKSI_CHOICES = [
    ('Top-up Saldo', 'Top-up Saldo'),
    ('Pembelian Stok', 'Pembelian Stok'),
    ('Penjualan Stok', 'Penjualan Stok'),
    ('Penyesuaian Saldo', 'Penyesuaian Saldo'),
]

class Counter(models.Model):
    """
    Model untuk menyimpan informasi detail tentang Counter Telkomsel.
    Setiap Counter terkait dengan satu User di sistem (pemilik/pengelola utama).
    """
    # Relasi One-to-One dengan Model User bawaan Django.
    # Jika user dihapus, data Counter terkait juga dihapus.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # Informasi Dasar Counter
    nama_counter = models.CharField(max_length=200, help_text="Nama resmi counter atau toko")
    nama_pemilik = models.CharField(max_length=200, help_text="Nama lengkap pemilik sesuai KTP")
    nomor_telepon = models.CharField(max_length=20, blank=True, null=True, help_text="Nomor telepon counter yang bisa dihubungi")
    alamat = models.TextField(help_text="Alamat lengkap lokasi counter")

    # Data Verifikasi (Termasuk Dokumen) - Membutuhkan Pillow
    foto_counter = models.ImageField(upload_to='counter_photos/', help_text="Foto tampak depan counter")
    ktp_pemilik = models.ImageField(upload_to='ktp_photos/', help_text="Foto KTP pemilik")
    selfie_dengan_ktp = models.ImageField(upload_to='selfie_ktp_photos/', help_text="Foto selfie pemilik memegang KTP")

    # Status Verifikasi
    status_verifikasi = models.CharField(
        max_length=20,
        choices=STATUS_VERIFIKASI_CHOICES,
        default='Pending',
        help_text="Status verifikasi data counter oleh admin"
    )
    tanggal_verifikasi = models.DateTimeField(null=True, blank=True, help_text="Tanggal dan waktu verifikasi selesai")
    notes_verifikasi = models.TextField(blank=True, null=True, help_text="Catatan dari admin terkait verifikasi")

    # Saldo Counter
    saldo = models.DecimalField(
        max_digits=15, # Total digit (misal: 15 angka)
        decimal_places=2, # 2 angka di belakang koma (untuk rupiah)
        default=0.00,
        help_text="Saldo digital counter untuk transaksi di sistem"
    )

    # Informasi Waktu
    tanggal_bergabung = models.DateTimeField(auto_now_add=True, help_text="Tanggal dan waktu pendaftaran counter")
    updated_at = models.DateTimeField(auto_now=True, help_text="Tanggal dan waktu terakhir data diupdate")

    def __str__(self):
        # Mengakses username dari objek User terkait
        return f"Counter: {self.nama_counter} ({self.user.username})"

    class Meta:
        verbose_name_plural = "Counters" # Nama yang muncul di Admin site (plural)
        ordering = ['tanggal_bergabung'] # Default sorting


class Product(models.Model):
    """
    Model untuk menyimpan informasi tentang produk Telkomsel yang dijual (Kartu, Voucher, dll).
    """
    nama_produk = models.CharField(max_length=100, unique=True, help_text="Nama unik produk")
    jenis_produk = models.CharField(max_length=50, help_text="Jenis produk")
    harga_beli_dari_admin = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Harga produk saat counter membeli dari sistem"
    )
    deskripsi = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Apakah produk ini masih tersedia?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_produk

    class Meta:
         ordering = ['nama_produk']


class CounterStock(models.Model):
    """
    Model untuk menyimpan jumlah stok produk tertentu yang dimiliki oleh Counter tertentu.
    """
    # ForeignKey ke Model Counter (One-to-Many: Satu Counter punya banyak Stok)
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='stock_items')
    # ForeignKey ke Model Product (One-to-Many: Satu Produk ada di banyak Stok Counter)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='counter_stocks')
    jumlah = models.PositiveIntegerField(default=0, help_text="Jumlah stok produk ini di counter")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Memastikan setiap Counter hanya memiliki satu entri untuk setiap Product
        unique_together = ('counter', 'product')
        verbose_name_plural = "Counter Stock"

    def __str__(self):
        return f"{self.counter.nama_counter} - {self.product.nama_produk}: {self.jumlah}"


class TopUpRequest(models.Model):
    """
    Model untuk mencatat permintaan top-up saldo oleh counter dan statusnya.
    """
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='topup_requests')
    jumlah_diminta = models.DecimalField(max_digits=15, decimal_places=2, help_text="Jumlah saldo yang diminta top-up")
    metode_pembayaran = models.CharField(max_length=100, help_text="Metode pembayaran")
    bukti_transfer = models.ImageField(upload_to='topup_proofs/', null=True, blank=True, help_text="Bukti transfer")
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Menunggu'), ('Approved', 'Disetujui'), ('Rejected', 'Ditolak')],
        default='Pending',
        help_text="Status permintaan top-up"
    )
    tanggal_request = models.DateTimeField(auto_now_add=True)
    tanggal_proses = models.DateTimeField(null=True, blank=True)
    # ForeignKey ke User yang memproses request (admin/petugas)
    diproses_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_topup_requests')
    notes_admin = models.TextField(blank=True, null=True, help_text="Catatan admin")

    def __str__(self):
        return f"Top-up request by {self.counter.nama_counter} - {self.jumlah_diminta} ({self.status})"

    class Meta:
        ordering = ['-tanggal_request']


class Transaction(models.Model):
    """
    Model untuk mencatat setiap transaksi (top-up, pembelian stok, dll).
    """
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='transactions')
    jenis_transaksi = models.CharField(max_length=50, choices=JENIS_TRANSAKSI_CHOICES)
    jumlah_saldo_berubah = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Perubahan saldo (positif: masuk, negatif: keluar)",
        default=0.00
    )
    # Jika transaksi terkait stok:
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    jumlah_produk_berubah = models.IntegerField(
        help_text="Perubahan jumlah produk (positif: tambah, negatif: kurang)",
        null=True,
        blank=True
    )

    tanggal_waktu = models.DateTimeField(auto_now_add=True)
    keterangan = models.TextField(blank=True, null=True)
    # Siapa yang mencatat/membuat transaksi (opsional, bisa jadi sistem atau admin)
    dicatat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_transactions')

    def __str__(self):
        return f"Transaksi {self.jenis_transaksi} oleh {self.counter.nama_counter}"

    class Meta:
        ordering = ['-tanggal_waktu'] # Transaksi terbaru di atas