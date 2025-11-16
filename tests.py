from django.test import TestCase
from django.contrib.auth.models import User
from investors.models import InvestorProfile, Document, AuditLog

class SimpleTests(TestCase):
    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_investor_profile_creation(self):
        """Test investor profile creation"""
        user = User.objects.create_user(
            username='investor1',
            email='investor@example.com', 
            password='testpass123'
        )
        profile = InvestorProfile.objects.create(
            user=user,
            phone_number='555-1234'
        )
        self.assertEqual(profile.user.username, 'investor1')
        self.assertFalse(profile.mfa_enabled)
    
    def test_audit_log_creation(self):
        """Test audit logging works"""
        user = User.objects.create_user(
            username='audittest',
            password='testpass123'
        )
        log = AuditLog.objects.create(
            user=user,
            action='TEST_ACTION',
            details='This is a test audit log'
        )
        self.assertEqual(log.action, 'TEST_ACTION')
        self.assertEqual(log.user, user)