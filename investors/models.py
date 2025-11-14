from django.db import models
from django.contrib.auth.models import User

class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    mfa_enabled = models.BooleanField(default=False)  # Placeholder for MFA logic

    def __str__(self):
        return self.user.username

class Document(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='next_versions')
    doc_type = models.CharField(max_length=50, choices=[
        ('id', 'ID'),
        ('statement', 'Statement'),
        ('agreement', 'Agreement'),
        ('other', 'Other'),
    ], default='other')

    def __str__(self):
        return f"{self.name} v{self.version} ({self.investor})"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} - {self.action}"