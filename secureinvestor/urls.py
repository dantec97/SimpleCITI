from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from investors.views import InvestorProfileViewSet, DocumentViewSet, AuditLogViewSet, login_with_mfa
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'investors', InvestorProfileViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'auditlogs', AuditLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/login/', login_with_mfa, name='login_with_mfa'),  # Add this line
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)