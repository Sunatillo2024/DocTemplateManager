from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Стандартная админка Django отключена (мы строим свою)
    # path('admin/', admin.site.urls),
    # API
    path('api/auth/', include('apps.accounts.urls')),
    path('api/templates/', include('apps.templates_app.urls')),
    path('api/admin/', include('apps.templates_app.admin_urls')),  # админские URL для шаблонов
    path('api/admin/', include('apps.accounts.admin_urls')),       # админские URL для пользователей
    path('api/documents/', include('apps.documents.urls')),

    # Фронтенд (отдаётся через шаблоны, можно сделать отдельное приложение или прямо здесь)
    path('', include('frontend.urls')),  # будем считать, что есть frontend/urls.py для рендеринга HTML
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)