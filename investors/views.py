from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Max, Q
from .models import InvestorProfile, Document, AuditLog
from .serializers import InvestorProfileSerializer, DocumentSerializer, AuditLogSerializer
import os
import pyotp
import qrcode
import io
import base64
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token

class InvestorProfileViewSet(viewsets.ModelViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view/edit investors

    # Add these MFA methods to InvestorProfileViewSet
    @action(detail=False, methods=['post'], url_path='mfa/setup', permission_classes=[permissions.IsAuthenticated])
    def setup_mfa(self, request):
        """Generate MFA secret and QR code"""
        user_profile = request.user.profile
        
        if user_profile.mfa_enabled:
            return Response({"error": "MFA already enabled"}, status=400)
        
        # Generate secret
        secret = pyotp.random_base32()
        user_profile.mfa_secret = secret
        user_profile.save()
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=request.user.email,
            issuer_name="SecureInvestor"
        )
        
        # Create QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code}",
            "message": "Scan QR code with Google Authenticator"
        })
    
    @action(detail=False, methods=['post'], url_path='mfa/verify', permission_classes=[permissions.IsAuthenticated])
    def verify_mfa(self, request):
        """Verify TOTP code and enable MFA"""
        user_profile = request.user.profile
        code = request.data.get('code')
        
        if not user_profile.mfa_secret:
            return Response({"error": "MFA not set up"}, status=400)
        
        totp = pyotp.TOTP(user_profile.mfa_secret)
        
        if totp.verify(code):
            user_profile.mfa_enabled = True
            user_profile.save()
            
            # Audit log
            AuditLog.objects.create(
                user=request.user,
                action="MFA_ENABLED",
                details="Multi-factor authentication enabled"
            )
            
            return Response({"message": "MFA enabled successfully"})
        else:
            return Response({"error": "Invalid code"}, status=400)
    
    @action(detail=False, methods=['post'], url_path='mfa/disable', permission_classes=[permissions.IsAuthenticated])
    def disable_mfa(self, request):
        """Disable MFA (requires current TOTP code)"""
        user_profile = request.user.profile
        code = request.data.get('code')
        
        if not user_profile.mfa_enabled:
            return Response({"error": "MFA not enabled"}, status=400)
        
        totp = pyotp.TOTP(user_profile.mfa_secret)
        
        if totp.verify(code):
            user_profile.mfa_enabled = False
            user_profile.mfa_secret = ''
            user_profile.save()
            
            # Audit log
            AuditLog.objects.create(
                user=request.user,
                action="MFA_DISABLED",
                details="Multi-factor authentication disabled"
            )
            
            return Response({"message": "MFA disabled successfully"})
        else:
            return Response({"error": "Invalid code"}, status=400)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Document.objects.all() if user.is_staff else Document.objects.filter(investor__user=user)

        # If ?all_versions=true, return all versions
        if self.request.query_params.get('all_versions', '').lower() == 'true':
            return base_queryset.order_by('-uploaded_at')

        # Only return latest version for each (investor, name, doc_type) combination
        # This is more efficient than the previous approach
        latest_versions = []
        
        # Get unique combinations of (investor, name, doc_type)
        unique_docs = base_queryset.values('investor', 'name', 'doc_type').distinct()
        
        for doc_combo in unique_docs:
            # Get the latest version for each combination
            latest_doc = base_queryset.filter(
                investor=doc_combo['investor'],
                name=doc_combo['name'],
                doc_type=doc_combo['doc_type']
            ).order_by('-version').first()
            
            if latest_doc:
                latest_versions.append(latest_doc.id)
        
        return base_queryset.filter(id__in=latest_versions).order_by('-uploaded_at')

    def perform_create(self, serializer):
        import boto3
        import uuid
        from django.core.files.base import ContentFile
        
        print("🚀 Starting Django document upload...")
        
        try:
            investor_profile = self.request.user.profile
            print(f"✅ Found investor profile: {investor_profile}")
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "User must have an investor profile to upload documents"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        name = serializer.validated_data['name']
        doc_type = serializer.validated_data['doc_type']
        file_obj = serializer.validated_data.get('file')
        
        print(f"📄 Document: {name}, type: {doc_type}, size: {file_obj.size} bytes")

        # Find the latest version
        latest_doc = (
            Document.objects
            .filter(investor=investor_profile, name=name, doc_type=doc_type)
            .order_by('-version')
            .first()
        )

        version = latest_doc.version + 1 if latest_doc else 1
        previous_version = latest_doc if latest_doc else None
        
        print(f"📈 Version: {version}")

        try:
            # Manual S3 upload
            print("📤 Uploading file directly to S3...")
            
            s3 = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_S3_REGION_NAME')
            )
            
            # Generate unique filename
            file_extension = file_obj.name.split('.')[-1] if '.' in file_obj.name else 'pdf'
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}.{file_extension}"
            s3_key = f"documents/{unique_filename}"
            
            # Read file content
            file_obj.seek(0)
            file_content = file_obj.read()
            
            # Upload to S3
            s3.put_object(
                Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'),
                Key=s3_key,
                Body=file_content,
                ServerSideEncryption='AES256',
                ContentType=file_obj.content_type or 'application/pdf'
            )
            
            print(f"✅ File uploaded to S3: {s3_key}")
            
            # Create document record with S3 path
            document = Document.objects.create(
                investor=investor_profile,
                name=name,
                doc_type=doc_type,
                version=version,
                previous_version=previous_version,
                file=s3_key  # Store the S3 key
            )
            
            print(f"✅ Document created: ID {document.id}")
            
            # Verify file exists in S3
            try:
                s3.head_object(Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'), Key=s3_key)
                print(f"✅ File confirmed in S3: {s3_key}")
            except Exception as check_error:
                print(f"❌ File verification failed: {check_error}")
            
        except Exception as e:
            print(f"❌ Error during upload: {e}")
            raise

        # Audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="UPLOAD",
            details=f"Uploaded document '{document.name}' (ID: {document.id}, version: {document.version})"
        )
        print("✅ Audit log created")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Audit log for download/view
        AuditLog.objects.create(
            user=request.user,
            action="DOWNLOAD",
            details=f"Downloaded/viewed document '{instance.name}' (ID: {instance.id}, version: {instance.version})"
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """Get all versions of a specific document"""
        instance = self.get_object()
        
        # Get all versions for this document's (investor, name, doc_type)
        versions = Document.objects.filter(
            investor=instance.investor,
            name=instance.name,
            doc_type=instance.doc_type
        ).order_by('-version')
        
        # Audit log for viewing history
        AuditLog.objects.create(
            user=request.user,
            action="VIEW_HISTORY",
            details=f"Viewed version history for document '{instance.name}'"
        )
        
        serializer = self.get_serializer(versions, many=True)
        return Response({
            'document_name': instance.name,
            'document_type': instance.doc_type,
            'total_versions': versions.count(),
            'versions': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='latest')
    def latest_documents(self, request):
        """Get only the latest version of each document"""
        # This is the same as the default queryset, but as an explicit endpoint
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-type/(?P<doc_type>[^/.]+)')
    def by_type(self, request, doc_type=None):
        """Get documents filtered by document type"""
        queryset = self.get_queryset().filter(doc_type=doc_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'document_type': doc_type,
            'count': queryset.count(),
            'documents': serializer.data
        })

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view logs
    
    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by('-timestamp')
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by action if specified
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action__icontains=action)
            
        return queryset

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_with_mfa(request):
    """Login with optional MFA verification"""
    username = request.data.get('username')
    password = request.data.get('password')
    mfa_code = request.data.get('mfa_code')
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({"error": "Invalid credentials"}, status=400)
    
    # Check if MFA is enabled
    if hasattr(user, 'profile') and user.profile.mfa_enabled:
        if not mfa_code:
            return Response({
                "mfa_required": True,
                "message": "MFA code required"
            }, status=200)
        
        # Verify MFA code
        totp = pyotp.TOTP(user.profile.mfa_secret)
        if not totp.verify(mfa_code):
            return Response({"error": "Invalid MFA code"}, status=400)
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    # Audit log
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        details=f"User logged in {'with MFA' if user.profile.mfa_enabled else 'without MFA'}"
    )
    
    return Response({
        "token": token.key,
        "user_id": user.id,
        "mfa_enabled": user.profile.mfa_enabled
    })