# SecureInvestor - Document Management System

A secure, enterprise-grade document management system built for financial services with multi-factor authentication, encrypted storage, and comprehensive audit logging.

## 🔐 Security Features

- **Multi-Factor Authentication (MFA)** - TOTP with Google Authenticator
- **Encrypted Document Storage** - AWS S3 with AES256 encryption
- **Token-Based Authentication** - Secure API access
- **Role-Based Permissions** - User/admin access control
- **Comprehensive Audit Logging** - All actions tracked for compliance

## 🚀 Key Features

- **Document Upload & Versioning** - Automatic version management
- **Secure File Storage** - AWS S3 integration with encryption
- **RESTful APIs** - Complete CRUD operations
- **Document History** - Track all versions of documents
- **Admin Dashboard** - Django admin for system management
- **Audit Trails** - Complete action logging for compliance

## 📋 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with optional MFA
- `POST /api/auth/token/` - Get authentication token

### MFA Management
- `POST /api/investors/mfa/setup/` - Generate MFA QR code
- `POST /api/investors/mfa/verify/` - Enable MFA
- `POST /api/investors/mfa/disable/` - Disable MFA

### Document Management
- `GET /api/documents/` - List documents (latest versions)
- `POST /api/documents/` - Upload new document
- `GET /api/documents/{id}/` - Get document details
- `GET /api/documents/{id}/history/` - Get document version history
- `GET /api/documents/by-type/{type}/` - Filter by document type

### Administration
- `GET /api/investors/` - Manage investor profiles (admin only)
- `GET /api/auditlogs/` - View audit logs (admin only)

## 🛠️ Technology Stack

- **Backend:** Django 5.2.8 + Django REST Framework
- **Database:** PostgreSQL
- **Storage:** AWS S3 with server-side encryption
- **Authentication:** Token Auth + TOTP MFA
- **Security:** pyotp, qrcode generation

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd secureinvestor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework psycopg2 boto3 pyotp qrcode[pil] python-dotenv
   ```

4. **Setup environment variables**
   Create `.env` file with:
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=True
   POSTGRES_DB=secureinvestor
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-password
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_STORAGE_BUCKET_NAME=your-s3-bucket
   AWS_S3_REGION_NAME=us-east-2
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## 🔒 Security Implementation

### Multi-Factor Authentication
- TOTP-based using Google Authenticator
- QR code generation for easy setup
- Time-based codes (30-second validity)

### Document Security
- Server-side encryption (AES256)
- Access-controlled storage
- No public bucket access

### Audit Compliance
- All user actions logged
- Timestamp and user tracking
- Admin-only audit log access

## 📱 MFA Setup Flow

1. User calls `/api/investors/mfa/setup/`
2. Scans returned QR code with Google Authenticator
3. Enters 6-digit code to verify setup
4. MFA enabled for future logins

## 🏢 Enterprise Features

- Document versioning with history tracking
- Role-based access control
- Comprehensive audit trails
- Encrypted file storage
- Secure API endpoints
- Professional error handling

---

*Built for enterprise-grade security and compliance requirements.*