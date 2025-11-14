from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Max, Q
from .models import InvestorProfile, Document, AuditLog
from .serializers import InvestorProfileSerializer, DocumentSerializer, AuditLogSerializer
import os

class InvestorProfileViewSet(viewsets.ModelViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view/edit investors

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