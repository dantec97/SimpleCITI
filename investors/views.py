from rest_framework import viewsets, permissions
from .models import InvestorProfile, Document, AuditLog
from .serializers import InvestorProfileSerializer, DocumentSerializer, AuditLogSerializer

class InvestorProfileViewSet(viewsets.ModelViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view/edit investors

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        # Attach the document to the current user's investor profile
        investor_profile = self.request.user.profile
        serializer.save(investor=investor_profile)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view logs