from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from investors.views import InvestorProfileViewSet, DocumentViewSet, AuditLogViewSet

router = routers.DefaultRouter()
router.register(r'investors', InvestorProfileViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'auditlogs', AuditLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
]