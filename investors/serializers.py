from rest_framework import serializers
from django.contrib.auth.models import User
from .models import InvestorProfile, Document, AuditLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InvestorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = InvestorProfile
        fields = ['id', 'user', 'phone_number', 'mfa_enabled']

class DocumentSerializer(serializers.ModelSerializer):
    investor = InvestorProfileSerializer(read_only=True)
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'investor', 'name', 'file', 'uploaded_at',
            'version', 'previous_version', 'doc_type'
        ]
        read_only_fields = ['uploaded_at', 'version']

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'timestamp', 'details']