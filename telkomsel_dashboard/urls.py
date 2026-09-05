# TelkomselCounterApp/telkomsel_main_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # URL otentikasi bawaan Django (login, logout, password reset, dll) di bawah /accounts/
    path('accounts/', include('django.contrib.auth.urls')),

    # Sertakan URL dari aplikasi 'counters'.
    # path('') artinya URL dari counters/urls.py akan diakses langsung dari root.
    # Contoh: /dashboard/ dan /register/
    path('', include('counters.urls')),
]

# Hanya melayani file media saat DEBUG=True (untuk development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Tambahkan ini jika Anda punya file static di STATICFILES_DIRS
    # from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # urlpatterns += staticfiles_urlpatterns()