<div align="center">

# Secure-Investor Backend

**A secure Django REST API for document management with MFA, audit logging, and S3 storage - designed for regulated industries.**

</div>

---

## 🚀 Demo & Features

### Admin Flow  
<img src="Assets/SimpleCiti_admin_flow1.gif" alt="Admin creates user" width="600"/>

**Admin User Management:**  
Admins log in and create investor accounts (no open registration). Each user gets an InvestorProfile. Admins can view and manage all users, documents, and audit logs from the admin panel.

---

### User Flow  
<img src="Assets/SimpleCiti_user_flow3.gif" alt="User login and MFA" width="600"/>

**User Login & MFA Enrollment:**  
Investors log in with credentials provided by the admin. On first login, they are prompted to set up MFA by scanning a QR code and entering a code from their authenticator app. MFA is required for all future logins.

---

### Admin: Documents View  
<img src="Assets/admin_docs_view.jpg" alt="Admin documents view" width="600"/>

**Secure Document Management:**  
Admins can view all documents uploaded by investors. Each document upload is versioned, and previous versions are preserved. Documents are stored securely in AWS S3.

---

### Admin: Audit Logs  
<img src="Assets/audit_logs.png" alt="Admin audit logs" width="600"/>

**Audit Logging:**  
All sensitive actions (login, MFA setup, document upload/download, etc.) are logged. Admins can view audit logs for compliance and security monitoring.

---

### AWS S3 Storage Example  
<img src="Assets/s3 screenshot.png" alt="AWS S3 Screenshot" width="600"/>

**AWS S3 Storage:**  
All documents are stored in AWS S3 with unique keys. Documents are encrypted at rest and only accessible via secure, temporary presigned URLs.

---

## ✨ Features

- **Admin User Management:**  
  Admins create investor accounts via Django admin or API. Each user gets an InvestorProfile.
- **Multi-Factor Authentication (MFA):**  
  TOTP-based MFA with QR code setup. Users self-enroll after first login.
- **Secure Document Management:**  
  Document upload with automatic versioning and S3 storage.  
  Pre-signed URLs for secure downloads.  
  Version history tracking with immutable previous versions.
- **Audit Logging:**  
  Comprehensive logging of all sensitive actions for compliance.
- **REST API:**  
  Full REST API with token authentication and role-based permissions.
- **Docker Support:**  
  Complete containerization with PostgreSQL database.

---

## 🛠️ Tech Stack

- **Backend:** Django 5.2.8, Django REST Framework
- **Database:** PostgreSQL 15
- **Storage:** AWS S3 (with server-side encryption)
- **Authentication:** Django Token Auth + TOTP MFA (PyOTP)
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Frontend:** [Secure-Investor React Frontend](https://github.com/dantec97/SimpleCITI_frontend) (separate repo)

---

## ⚡ Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (or Docker)
- AWS S3 bucket with appropriate permissions
- Environment variables (see `.env.example`)

### Installation

```bash
git clone https://github.com/dantec97/SimpleCITI.git
cd SimpleCITI
```

**Option 1: Docker (Recommended)**
```bash
# Copy environment file and configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# Start with Docker Compose
docker-compose up --build
```

**Option 2: Local Development**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and AWS credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The API will be available at [http://localhost:8000/api/](http://localhost:8000/api/).

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with optional MFA
- `POST /api/auth/token/` - Get auth token (standard Django)

### User Management (Admin Only)
- `GET /api/investors/` - List all investor profiles
- `POST /api/investors/create_user/` - Create new user account
- `GET /api/investors/{id}/` - Get specific investor profile

### MFA Management
- `POST /api/investors/mfa/setup/` - Generate MFA secret and QR code
- `POST /api/investors/mfa/verify/` - Verify TOTP code and enable MFA
- `POST /api/investors/mfa/disable/` - Disable MFA (requires current code)

### Document Management
- `GET /api/documents/` - List documents (latest versions only)
- `POST /api/documents/` - Upload new document
- `GET /api/documents/{id}/` - Get document details
- `GET /api/documents/{id}/download/` - Get secure download URL
- `GET /api/documents/{id}/history/` - Get all versions of a document
- `GET /api/documents/latest/` - Explicitly get latest versions
- `GET /api/documents/by-type/{type}/` - Filter by document type

### Audit Logging (Admin Only)
- `GET /api/auditlogs/` - List audit logs
- `GET /api/auditlogs/?user_id={id}` - Filter by user
- `GET /api/auditlogs/?action={action}` - Filter by action

---

## 🔐 Security Implementation

### Multi-Factor Authentication
- **TOTP-based:** Uses PyOTP for time-based one-time passwords
- **QR Code Setup:** Automatic QR code generation for authenticator apps
- **User-Driven:** Users set up MFA themselves, not admin-forced
- **Backup Codes:** JSON field for future backup code implementation

### Document Security
- **S3 Storage:** All documents stored in AWS S3 with server-side encryption
- **Unique Keys:** Each document version gets a unique S3 key (prevents overwrites)
- **Pre-signed URLs:** Temporary, secure download links (5-minute expiry)
- **Version Control:** Immutable previous versions with proper linking

### Access Control
- **Token Authentication:** Required for all API endpoints
- **Role-Based Permissions:** Admin vs. user access levels
- **Document Isolation:** Users can only access their own documents
- **CORS Protection:** Configured for specific frontend origins

### Audit Trail
- **Comprehensive Logging:** All sensitive actions logged automatically
- **User Attribution:** Every log entry tied to specific user
- **Timestamp Tracking:** Precise timing of all actions
- **Searchable:** Logs can be filtered by user or action type

---

## 🧑‍💼 Usage

### Admin Workflow
1. Log in to Django admin panel (`/admin/`)
2. Create user accounts with required email addresses
3. View all documents, users, and audit logs
4. Monitor system activity via audit logs

### Investor Workflow
1. Log in with admin-provided credentials
2. Set up MFA on first login (scan QR code)
3. Upload documents (automatic versioning)
4. View and download document versions
5. Manage MFA settings as needed

### Document Versioning
- Same name + document type = new version
- Different name or type = new document
- Each version maintains its own S3 file
- Version history accessible via API

---

## 🐳 Docker Deployment

```yaml
# docker-compose.yml includes:
services:
  db:          # PostgreSQL 15 database
  web:         # Django app with Gunicorn
```

**Environment Variables:**
- Database credentials and connection
- AWS S3 credentials and bucket info  
- Django secret key and debug settings
- CORS allowed origins

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test investors.tests.SimpleTests

# With coverage (if installed)
coverage run --source='.' manage.py test
coverage report
```

**CI/CD:** GitHub Actions automatically runs tests on push/PR.

---

## 📁 Project Structure

```
secureinvestor/
├── investors/           # Main Django app
│   ├── models.py       # User profiles, documents, audit logs
│   ├── views.py        # API viewsets and MFA logic
│   ├── serializers.py  # DRF serializers
│   ├── admin.py        # Django admin configuration
│   └── tests.py        # Unit tests
├── secureinvestor/     # Django project settings
│   ├── settings.py     # Configuration and AWS setup
│   └── urls.py         # URL routing
├── Assets/             # Demo images/GIFs
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Container orchestration
└── .github/workflows/  # CI/CD configuration
```

---

## 🔒 Security Notes

- **No open registration:** Only admins can create user accounts
- **MFA enforcement:** Users must set up MFA before document access
- **S3 encryption:** All documents encrypted at rest (AES-256)
- **Pre-signed URLs:** Temporary, secure access to documents
- **Environment variables:** No secrets in codebase
- **Audit logging:** Complete action history for compliance
- **CORS configuration:** Restricted to trusted origins
- **Token expiration:** Implement token rotation for production

---

## 🚀 Production Considerations

### Missing for Production
- **OAuth Integration:** Add social auth or enterprise SSO
- **Secrets Management:** Integrate AWS Secrets Manager or HashiCorp Vault
- **Advanced Monitoring:** Add Sentry for error tracking, Prometheus for metrics
- **Rate Limiting:** Implement API rate limiting
- **Backup Strategy:** Automated database and S3 backups
- **Load Balancing:** Multi-instance deployment with load balancer

### Recommended Additions
- **API Documentation:** Swagger/OpenAPI specification
- **Health Checks:** Kubernetes/Docker health check endpoints
- **Log Aggregation:** Centralized logging (ELK stack, CloudWatch)
- **Performance Monitoring:** APM tools for Django performance
- **Security Scanning:** Automated vulnerability assessments

---

## 📄 License

MIT License

---

## 📬 Contact

For questions or support, contact [dantecpriority@gmail.com](mailto:dantecpriority@gmail.com).

---

<div align="center">

**This Django backend provides enterprise-grade security and auditability for sensitive document management, making it ideal for financial services and other regulated industries.**

</div>