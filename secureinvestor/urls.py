from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from investors.views import InvestorProfileViewSet, DocumentViewSet, AuditLogViewSet

router = routers.DefaultRouter()
router.register(r'investors', InvestorProfileViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'auditlogs', AuditLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]