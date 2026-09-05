# TelkomselCounterApp/counters/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.contrib.auth import get_user_model # Cara lebih baik untuk mendapatkan model User
from .models import Counter

User = get_user_model() # Dapatkan model User aktif

class CounterRegistrationForm(UserCreationForm):
    """
    Form kustom untuk pendaftaran User dan Counter secara bersamaan.
    Mewarisi UserCreationForm untuk handling username dan password.
    """
    # Field tambahan untuk Model Counter
    nama_counter = forms.CharField(max_length=200, label="Nama Counter")
    nama_pemilik = forms.CharField(max_length=200, label="Nama Pemilik (sesuai KTP)")
    nomor_telepon = forms.CharField(max_length=20, required=False, label="Nomor Telepon Counter")
    alamat = forms.CharField(widget=forms.Textarea, label="Alamat Lengkap Counter")
    foto_counter = forms.ImageField(label="Foto Counter (Tampak Depan)")
    ktp_pemilik = forms.ImageField(label="Foto KTP Pemilik")
    selfie_dengan_ktp = forms.ImageField(label="Foto Selfie dengan KTP")

    class Meta(UserCreationForm.Meta):
        # Meta ini mengkonfigurasi bagian UserCreationForm, jadi merujuk ke Model User
        model = User
        # fields dari UserCreationForm.Meta sudah otomatis termasuk username, password, password2

    @transaction.atomic # Pastikan User dan Counter tersimpan bersamaan, atau batal semua jika ada error
    def save(self, commit=True):
        # Simpan User baru dari UserCreationForm (tapi belum di-commit ke DB)
        user = super().save(commit=False)
        user.save() # Simpan User ke database

        # Buat objek Counter baru menggunakan data dari form dan user yang baru dibuat
        counter = Counter.objects.create(
            user=user, # Hubungkan dengan user yang baru saja disimpan
            nama_counter=self.cleaned_data['nama_counter'],
            nama_pemilik=self.cleaned_data['nama_pemilik'],
            nomor_telepon=self.cleaned_data.get('nomor_telepon'), # Gunakan .get() untuk field optional
            alamat=self.cleaned_data['alamat'],
            foto_counter=self.cleaned_data['foto_counter'],
            ktp_pemilik=self.cleaned_data['ktp_pemilik'],
            selfie_dengan_ktp=self.cleaned_data['selfie_dengan_ktp'],
            # status_verifikasi otomatis default 'Pending' sesuai Model
            # saldo otomatis default 0.00 sesuai Model
        )

        # UserCreationForm.save() mengembalikan objek user yang baru dibuat
        return user