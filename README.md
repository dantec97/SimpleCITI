<div align="center">

# Secure-Investor Frontend

**A modern React frontend for Secure-Investor: Secure, auditable, and user-friendly document management for regulated industries.**

</div>

---

## 🚀 Demo

### Admin Flow  
<img src="Assets/SimpleCiti_admin_flow1.gif" alt="Admin creates user" width="600"/>

### User Flow  
<img src="Assets/SimpleCiti_user_flow3.gif" alt="User login and MFA" width="600"/>

### Admin: Documents View  
<img src="Assets/admin_docs_view.jpg" alt="Admin documents view" width="600"/>

### Admin: Audit Logs  
<img src="Assets/audit_logs.png" alt="Admin audit logs" width="600"/>

### AWS S3 Storage Example  
<img src="Assets/s3 screenshot.png" alt="AWS S3 Screenshot" width="600"/>

---

## ✨ Features

- **Admin User Management:**  
  Admins create investor accounts (no open registration). Each user gets an InvestorProfile.
- **Multi-Factor Authentication (MFA):**  
  Users must set up MFA on first login (QR code + TOTP). MFA is required for all logins.
- **Secure Document Management:**  
  Investors upload documents (ID, statements, agreements, etc).  
  Each upload is versioned; previous versions are preserved.  
  Documents are stored securely in AWS S3.  
  Users can view and download current and previous versions.
- **Audit Logging:**  
  All sensitive actions (login, MFA, upload, download, etc) are logged.  
  Admins can view audit logs.
- **Admin Panel:**  
  Admins can view and manage users, documents, and logs.
- **Modern UI/UX:**  
  Responsive, dark-themed design with blue accent.  
  Clear feedback for all actions.  
  Consistent, accessible styling across all pages.

---

## 🛠️ Tech Stack

- **Frontend:** React 18, React Router, Fetch API
- **Styling:** Custom CSS (`src/Styles/Styles.css`)
- **Backend:** [Secure-Investor Django API](https://github.com/dantec97/SimpleCITI) (required)
- **Storage:** AWS S3 (for documents)
- **Auth:** Django Token Auth + TOTP MFA

---

## ⚡ Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- npm or yarn
- Access to the Secure-Investor Django backend (running locally or remotely)

### Installation

```bash
git clone https://github.com/dantec97/SimpleCITI_frontend.git
cd secure-investor-frontend
npm install
# or
yarn install
```

**Configure API endpoint:**  
By default, the frontend expects the backend at `http://localhost:8000/api`.  
To change this, edit `src/api/api.js` and update `API_BASE`.

**Start the development server:**
```bash
npm run dev
# or
yarn dev
```
The app will be available at [http://localhost:5173](http://localhost:5173).

---

## 🧑‍💼 Usage

### Admin Flow
1. Log in as an admin (create via Django admin if needed).
2. Use the Admin Panel to create new investor users.
3. View all users, documents, and audit logs.

### Investor Flow
1. Log in with credentials provided by admin.
2. On first login, set up MFA by scanning the QR code and entering a code from your authenticator app.
3. Upload documents (ID, statements, etc).
4. Uploading a document with the same name and type creates a new version.
5. View and download current and previous versions.
6. Manage MFA from the profile settings.

### Security
- All API requests require a valid token.
- MFA is enforced for all users.
- Documents are stored in S3 with unique keys and are only accessible via presigned URLs.
- All sensitive actions are logged for audit/compliance.

---

## 📁 Project Structure

```
src/
  api/           # API helper functions
  components/    # React components (Login, MFA, DocumentList, Admin, etc)
  Styles/        # CSS files (main theme, login, etc)
  App.jsx        # Main app component
  main.jsx       # Entry point
```

---

## 🎨 Customization

- **Branding:**  
  Update colors and logo in `src/Styles/Styles.css` and header in `App.jsx`.
- **API Endpoint:**  
  Change `API_BASE` in `src/api/api.js` if your backend is not at `localhost:8000`.
- **Document Types:**  
  Edit the options in `DocumentUpload.jsx` to add/remove document types.

---

## 🔒 Security Notes

- **No open registration:** Only admins can create users.
- **MFA enforced:** Users must set up MFA before accessing documents.
- **Token Auth:** All API endpoints require a valid token.
- **S3 Storage:** Documents are encrypted at rest and only accessible via presigned URLs.
- **CORS:** Only trusted frontend origins should be allowed in backend settings.
- **No secrets in code:** All secrets and keys are managed via environment variables on the backend.

---

## 📝 Demo Script (for Interviews)

1. **Admin logs in and creates a new user.**
2. **User logs in, sets up MFA.**
3. **User uploads a document, then uploads a new version.**
4. **User downloads both versions.**
5. **Admin views audit logs.**
6. **User disables MFA from profile settings.**

---

## 🛠️ Troubleshooting

- **Cannot connect to backend:**  
  Ensure the Django API is running and CORS is configured to allow your frontend.
- **File upload/download issues:**  
  Check S3 credentials and bucket permissions on the backend.
- **MFA not working:**  
  Ensure your device time is correct and you are using the correct code from your authenticator app.

---

## 📄 License

MIT License

---

## 📬 Contact

For questions or support, contact [dantecpriority@gmail.com](mailto:dantecpriority@gmail.com).

---

<div align="center">

**This app provides a secure, auditable, and user-friendly way for investors to manage sensitive documents, with strong authentication, version control, and full admin oversight—making it ideal for regulated industries.**

</div>