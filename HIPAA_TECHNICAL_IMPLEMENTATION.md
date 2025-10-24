# 🔧 HIPAA TECHNICAL IMPLEMENTATION GUIDE
## The Christman AI Project - AlphaWolf & AlphaVox

**Document Version:** 1.0  
**Last Updated:** October 24, 2025  
**Audience:** Software Engineers, DevOps, Security Engineers  
**Prerequisite:** Read HIPAA_COMPLIANCE_FRAMEWORK.md

---

## 📋 Overview

This document provides step-by-step technical implementation guidance for HIPAA compliance
in AlphaWolf and AlphaVox systems. It translates regulatory requirements into concrete
code, configuration, and infrastructure changes.

---

## 🗄️ 1. DATABASE ENCRYPTION

### 1.1 SQLAlchemy Encryption Configuration

**Install Required Packages:**
```bash
pip install cryptography sqlalchemy-utils
```

**Create Encryption Service:**
```python
# File: services/encryption_service.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import os
import base64

class PHIEncryptionService:
    """
    HIPAA-compliant encryption service for Protected Health Information
    
    Uses AES-256 via Fernet (symmetric encryption)
    Keys stored in AWS KMS or environment variables (development only)
    """
    
    def __init__(self):
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self) -> bytes:
        """
        Retrieve encryption key from secure storage
        
        PRODUCTION: Use AWS KMS, Azure Key Vault, or Google Cloud KMS
        DEVELOPMENT: Use environment variable (NOT FOR PRODUCTION)
        """
        if os.getenv('ENV') == 'production':
            # AWS KMS integration
            import boto3
            kms = boto3.client('kms', region_name=os.getenv('AWS_DEFAULT_REGION'))
            key_id = os.getenv('KMS_KEY_ID')
            
            # Generate data key from KMS
            response = kms.generate_data_key(KeyId=key_id, KeySpec='AES_256')
            return base64.urlsafe_b64encode(response['Plaintext'][:32])
        else:
            # Development: use environment variable
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                # Generate new key for development
                key = Fernet.generate_key()
                print(f"WARNING: Generated new encryption key: {key.decode()}")
                print("Set ENCRYPTION_KEY environment variable to persist this key")
            elif isinstance(key, str):
                key = key.encode()
            return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: Sensitive data to encrypt
        
        Returns:
            Base64-encoded encrypted string
        """
        if plaintext is None:
            return None
        
        encrypted_bytes = self.cipher.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string
        
        Args:
            ciphertext: Encrypted data
        
        Returns:
            Decrypted plaintext string
        """
        if ciphertext is None:
            return None
        
        decrypted_bytes = self.cipher.decrypt(ciphertext.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')

# Global encryption service instance
phi_encryption = PHIEncryptionService()
```

### 1.2 Encrypted Database Columns

**Update models.py to encrypt PHI fields:**
```python
# File: models.py (add to existing User model)

from sqlalchemy.ext.hybrid import hybrid_property
from services.encryption_service import phi_encryption

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Encrypted PHI fields
    _full_name = db.Column('full_name', db.Text)  # Encrypted
    _date_of_birth = db.Column('date_of_birth', db.Text)  # Encrypted
    _ssn = db.Column('ssn', db.Text)  # Encrypted
    _medical_record_number = db.Column('medical_record_number', db.Text)  # Encrypted
    _phone_number = db.Column('phone_number', db.Text)  # Encrypted
    _address = db.Column('address', db.Text)  # Encrypted
    
    # Hybrid properties for transparent encryption/decryption
    @hybrid_property
    def full_name(self):
        return phi_encryption.decrypt(self._full_name) if self._full_name else None
    
    @full_name.setter
    def full_name(self, value):
        self._full_name = phi_encryption.encrypt(value) if value else None
    
    @hybrid_property
    def date_of_birth(self):
        encrypted = self._date_of_birth
        if encrypted:
            decrypted = phi_encryption.decrypt(encrypted)
            return datetime.fromisoformat(decrypted)
        return None
    
    @date_of_birth.setter
    def date_of_birth(self, value):
        if value:
            iso_string = value.isoformat()
            self._date_of_birth = phi_encryption.encrypt(iso_string)
        else:
            self._date_of_birth = None
    
    @hybrid_property
    def ssn(self):
        return phi_encryption.decrypt(self._ssn) if self._ssn else None
    
    @ssn.setter
    def ssn(self, value):
        self._ssn = phi_encryption.encrypt(value) if value else None
    
    # Repeat for other PHI fields...

class MedicalHistory(db.Model):
    """Store medical history with encryption"""
    __tablename__ = 'medical_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Encrypted fields
    _diagnosis = db.Column('diagnosis', db.Text)
    _medications = db.Column('medications', db.Text)
    _allergies = db.Column('allergies', db.Text)
    _notes = db.Column('notes', db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    @hybrid_property
    def diagnosis(self):
        return phi_encryption.decrypt(self._diagnosis) if self._diagnosis else None
    
    @diagnosis.setter
    def diagnosis(self, value):
        self._diagnosis = phi_encryption.encrypt(value) if value else None
    
    # Repeat for other PHI fields...
```

### 1.3 Database Migration for Encryption

**Create migration to encrypt existing data:**
```python
# File: migrations/encrypt_existing_phi.py

from flask import Flask
from models import db, User, MedicalHistory
from services.encryption_service import phi_encryption

def encrypt_existing_records():
    """
    One-time migration: Encrypt existing plaintext PHI
    
    WARNING: Backup database before running!
    """
    app = Flask(__name__)
    app.config.from_object('config.ProductionConfig')
    
    with app.app_context():
        db.init_app(app)
        
        # Encrypt User PHI
        users = User.query.all()
        for user in users:
            # Check if already encrypted (encrypted data has Fernet prefix)
            if user._full_name and not user._full_name.startswith(b'gAAAAA'):
                user.full_name = user._full_name  # Setter will encrypt
            if user._date_of_birth and not user._date_of_birth.startswith(b'gAAAAA'):
                # Parse existing date, then re-set (will encrypt)
                dob_str = user._date_of_birth
                user.date_of_birth = datetime.fromisoformat(dob_str)
            # Repeat for other fields...
        
        # Encrypt MedicalHistory PHI
        histories = MedicalHistory.query.all()
        for history in histories:
            if history._diagnosis and not history._diagnosis.startswith(b'gAAAAA'):
                history.diagnosis = history._diagnosis
            # Repeat for other fields...
        
        db.session.commit()
        print("✅ Successfully encrypted all existing PHI")

if __name__ == '__main__':
    # Confirm before running
    response = input("⚠️  This will encrypt all PHI in the database. Continue? (yes/no): ")
    if response.lower() == 'yes':
        encrypt_existing_records()
    else:
        print("Aborted.")
```

### 1.4 PostgreSQL Encryption at Rest (AWS RDS)

**Enable AWS RDS encryption:**
```bash
# AWS CLI command to enable encryption on new RDS instance
aws rds create-db-instance \
    --db-instance-identifier alphawolf-production \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --master-username admin \
    --master-user-password <SECURE_PASSWORD> \
    --allocated-storage 100 \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID \
    --backup-retention-period 30 \
    --vpc-security-group-ids sg-XXXXXXXXX
```

**For existing RDS instance (requires snapshot restore):**
```bash
# 1. Create encrypted snapshot
aws rds create-db-snapshot \
    --db-instance-identifier alphawolf-production \
    --db-snapshot-identifier alphawolf-pre-encryption-snapshot

# 2. Copy snapshot with encryption
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier alphawolf-pre-encryption-snapshot \
    --target-db-snapshot-identifier alphawolf-encrypted-snapshot \
    --kms-key-id arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID \
    --copy-tags

# 3. Restore from encrypted snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier alphawolf-production-encrypted \
    --db-snapshot-identifier alphawolf-encrypted-snapshot \
    --storage-encrypted
```

---

## 🔐 2. ACCESS CONTROLS & AUTHENTICATION

### 2.1 Multi-Factor Authentication (MFA)

**Install PyOTP for TOTP:**
```bash
pip install pyotp qrcode[pil]
```

**Add MFA to User model:**
```python
# File: models.py (extend User model)

import pyotp
import qrcode
from io import BytesIO
import base64

class User(db.Model):
    # ... existing fields ...
    
    mfa_enabled = db.Column(db.Boolean, default=False)
    _mfa_secret = db.Column('mfa_secret', db.Text)  # Encrypted
    mfa_backup_codes = db.Column(db.Text)  # Encrypted JSON array
    
    @hybrid_property
    def mfa_secret(self):
        return phi_encryption.decrypt(self._mfa_secret) if self._mfa_secret else None
    
    @mfa_secret.setter
    def mfa_secret(self, value):
        self._mfa_secret = phi_encryption.encrypt(value) if value else None
    
    def generate_mfa_secret(self):
        """Generate new MFA secret and backup codes"""
        self.mfa_secret = pyotp.random_base32()
        
        # Generate 10 backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        encrypted_codes = phi_encryption.encrypt(json.dumps(backup_codes))
        self.mfa_backup_codes = encrypted_codes
        
        return self.mfa_secret, backup_codes
    
    def get_mfa_qr_code(self):
        """Generate QR code for MFA setup"""
        totp_uri = pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email,
            issuer_name='AlphaWolf'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def verify_mfa_token(self, token: str) -> bool:
        """Verify MFA token or backup code"""
        if not self.mfa_enabled:
            return True  # MFA not enabled, pass through
        
        # Try TOTP token
        totp = pyotp.TOTP(self.mfa_secret)
        if totp.verify(token, valid_window=1):
            return True
        
        # Try backup codes
        if self.mfa_backup_codes:
            backup_codes = json.loads(phi_encryption.decrypt(self.mfa_backup_codes))
            if token in backup_codes:
                # Remove used backup code
                backup_codes.remove(token)
                self.mfa_backup_codes = phi_encryption.encrypt(json.dumps(backup_codes))
                db.session.commit()
                return True
        
        return False
```

**MFA Endpoints:**
```python
# File: app.py or auth_routes.py

from flask_login import login_user, current_user, login_required

@app.route('/api/auth/mfa/setup', methods=['POST'])
@login_required
def setup_mfa():
    """Initiate MFA setup for current user"""
    secret, backup_codes = current_user.generate_mfa_secret()
    qr_code = current_user.get_mfa_qr_code()
    
    # Don't enable MFA yet (wait for verification)
    db.session.commit()
    
    return jsonify({
        'qr_code': qr_code,
        'secret': secret,
        'backup_codes': backup_codes,
        'instructions': 'Scan QR code with authenticator app, then verify token'
    })

@app.route('/api/auth/mfa/verify', methods=['POST'])
@login_required
def verify_mfa_setup():
    """Verify MFA token and enable MFA"""
    token = request.json.get('token')
    
    if current_user.verify_mfa_token(token):
        current_user.mfa_enabled = True
        db.session.commit()
        
        audit_logger.log_security_event(
            event_type='MFA_ENABLED',
            severity='INFO',
            details={'user_id': current_user.id}
        )
        
        return jsonify({'success': True, 'message': 'MFA enabled'})
    else:
        return jsonify({'success': False, 'error': 'Invalid token'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with username/password and optional MFA"""
    username = request.json.get('username')
    password = request.json.get('password')
    mfa_token = request.json.get('mfa_token')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        # Log failed attempt
        audit_logger.log_security_event(
            event_type='LOGIN_FAILED',
            severity='WARNING',
            details={'username': username, 'reason': 'invalid_credentials'}
        )
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if account is locked
    if user.account_locked:
        return jsonify({'error': 'Account locked. Contact administrator.'}), 403
    
    # Check MFA if enabled
    if user.mfa_enabled:
        if not mfa_token:
            return jsonify({'mfa_required': True}), 200
        
        if not user.verify_mfa_token(mfa_token):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.account_locked = True
            db.session.commit()
            
            return jsonify({'error': 'Invalid MFA token'}), 401
    
    # Successful login
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    login_user(user)
    
    audit_logger.log_security_event(
        event_type='LOGIN_SUCCESS',
        severity='INFO',
        details={'user_id': user.id, 'mfa_used': user.mfa_enabled}
    )
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'token': generate_jwt_token(user)  # If using JWT
    })
```

### 2.2 Role-Based Access Control (RBAC)

**Define permission decorator:**
```python
# File: services/access_control.py

from functools import wraps
from flask import abort
from flask_login import current_user

class Permission:
    """Permission constants"""
    VIEW_OWN_DATA = 0x01
    EDIT_OWN_DATA = 0x02
    VIEW_ASSIGNED_PATIENTS = 0x04
    EDIT_ASSIGNED_PATIENTS = 0x08
    VIEW_ALL_PATIENTS = 0x10
    MANAGE_USERS = 0x20
    ACCESS_ADMIN = 0x40
    VIEW_AUDIT_LOGS = 0x80

class Role:
    """Role definitions with permissions"""
    PATIENT = Permission.VIEW_OWN_DATA | Permission.EDIT_OWN_DATA
    
    CAREGIVER = (Permission.VIEW_OWN_DATA | 
                 Permission.EDIT_OWN_DATA |
                 Permission.VIEW_ASSIGNED_PATIENTS |
                 Permission.EDIT_ASSIGNED_PATIENTS)
    
    CLINICIAN = (Permission.VIEW_ASSIGNED_PATIENTS |
                 Permission.EDIT_ASSIGNED_PATIENTS)
    
    ADMIN = 0xFF  # All permissions

def permission_required(permission):
    """Decorator to check if user has required permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            if not current_user.has_permission(permission):
                audit_logger.log_security_event(
                    event_type='PERMISSION_DENIED',
                    severity='WARNING',
                    details={
                        'user_id': current_user.id,
                        'required_permission': permission,
                        'endpoint': request.endpoint
                    }
                )
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage example
@app.route('/api/admin/users', methods=['GET'])
@login_required
@permission_required(Permission.MANAGE_USERS)
def list_users():
    """Admin-only endpoint to list all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/patient/<int:patient_id>/medical-history', methods=['GET'])
@login_required
def get_medical_history(patient_id):
    """Get patient's medical history (with access control)"""
    
    # Check if user can access this patient's data
    if current_user.id == patient_id:
        # Patient viewing own data
        pass
    elif current_user.has_permission(Permission.VIEW_ALL_PATIENTS):
        # Admin or clinician with full access
        pass
    elif current_user.has_permission(Permission.VIEW_ASSIGNED_PATIENTS):
        # Check if patient is assigned to this caregiver/clinician
        assignment = PatientAssignment.query.filter_by(
            caregiver_id=current_user.id,
            patient_id=patient_id
        ).first()
        if not assignment:
            audit_logger.log_security_event(
                event_type='UNAUTHORIZED_PHI_ACCESS_ATTEMPT',
                severity='WARNING',
                details={
                    'user_id': current_user.id,
                    'patient_id': patient_id,
                    'endpoint': request.endpoint
                }
            )
            abort(403)
    else:
        abort(403)
    
    # Log PHI access
    audit_logger.log_phi_access(
        user_id=current_user.id,
        patient_id=patient_id,
        action='READ',
        resource='medical_history',
        outcome='SUCCESS'
    )
    
    history = MedicalHistory.query.filter_by(user_id=patient_id).all()
    return jsonify([h.to_dict() for h in history])
```

### 2.3 Session Management & Automatic Logout

**Configure Flask session security:**
```python
# File: config.py

class ProductionConfig:
    # Session security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)  # Auto-logout after 15min
    SESSION_REFRESH_EACH_REQUEST = True  # Extend session on activity
    
    # Strong session secret
    SECRET_KEY = os.getenv('SESSION_SECRET')
    
    # Additional security headers
    TALISMAN_CONFIG = {
        'force_https': True,
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,
        'content_security_policy': {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'"],  # Consider removing unsafe-inline
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", 'data:', 'https:'],
            'font-src': ["'self'"],
            'connect-src': ["'self'"],
            'frame-ancestors': ["'none'"]
        }
    }
```

**Implement activity-based session timeout:**
```python
# File: app.py

from flask import session
from datetime import datetime, timedelta

@app.before_request
def check_session_timeout():
    """
    Check for user inactivity and enforce automatic logout
    """
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            timeout = timedelta(minutes=15)
            
            if datetime.utcnow() - last_activity_time > timeout:
                # Session timed out
                audit_logger.log_security_event(
                    event_type='SESSION_TIMEOUT',
                    severity='INFO',
                    details={'user_id': current_user.id}
                )
                
                logout_user()
                session.clear()
                return jsonify({'error': 'Session expired due to inactivity'}), 401
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
```

---

## 📊 3. AUDIT LOGGING SYSTEM

### 3.1 Database Schema for Audit Logs

**Create audit_logs table:**
```python
# File: models.py

class AuditLog(db.Model):
    """HIPAA-compliant audit log for all PHI access"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)  # PHI_ACCESS, LOGIN, etc.
    action = db.Column(db.String(20))  # READ, WRITE, DELETE, UPDATE
    outcome = db.Column(db.String(20))  # SUCCESS, FAILURE, DENIED
    
    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    username = db.Column(db.String(80))
    user_role = db.Column(db.String(50))
    
    # Patient information (for PHI access)
    patient_id = db.Column(db.Integer, index=True)
    
    # Resource accessed
    resource_type = db.Column(db.String(50))  # medical_history, patient_profile, etc.
    resource_id = db.Column(db.String(100))
    
    # Network information
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # Additional details (JSON)
    details = db.Column(db.JSON)
    
    # Integrity check
    checksum = db.Column(db.String(64))  # SHA-256 hash
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate checksum for tamper detection
        self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self):
        """Generate SHA-256 checksum of log entry"""
        data = f"{self.timestamp}|{self.event_type}|{self.user_id}|{self.patient_id}|{self.action}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_integrity(self):
        """Check if log entry has been tampered with"""
        return self.checksum == self.calculate_checksum()
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'action': self.action,
            'outcome': self.outcome,
            'user_id': self.user_id,
            'username': self.username,
            'patient_id': self.patient_id,
            'resource_type': self.resource_type,
            'ip_address': self.ip_address,
            'details': self.details
        }
```

### 3.2 Automatic Audit Logging Middleware

**Flask middleware for automatic PHI access logging:**
```python
# File: middleware/audit_middleware.py

from flask import request, g
from models import AuditLog, db

PHI_ENDPOINTS = [
    '/api/patient',
    '/api/memory-lane',
    '/api/medical-history',
    '/api/caregiver/patients'
]

@app.before_request
def log_phi_access_start():
    """Log start of PHI access request"""
    if any(endpoint in request.path for endpoint in PHI_ENDPOINTS):
        g.phi_access_start_time = datetime.utcnow()

@app.after_request
def log_phi_access_complete(response):
    """Log completion of PHI access request"""
    if hasattr(g, 'phi_access_start_time'):
        # Extract patient_id from URL or request body
        patient_id = request.view_args.get('patient_id') or request.json.get('patient_id')
        
        audit_log = AuditLog(
            event_type='PHI_ACCESS',
            action=request.method,
            outcome='SUCCESS' if response.status_code < 400 else 'FAILURE',
            user_id=current_user.id if current_user.is_authenticated else None,
            username=current_user.username if current_user.is_authenticated else 'anonymous',
            user_role=current_user.role if current_user.is_authenticated else None,
            patient_id=patient_id,
            resource_type=request.endpoint,
            resource_id=request.path,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            session_id=session.get('session_id'),
            details={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': (datetime.utcnow() - g.phi_access_start_time).total_seconds() * 1000
            }
        )
        
        db.session.add(audit_log)
        db.session.commit()
    
    return response
```

### 3.3 Audit Log Retention & Archival

**Automated log archival script:**
```python
# File: scripts/archive_audit_logs.py

import gzip
import json
from datetime import datetime, timedelta
from models import AuditLog, db

def archive_old_logs(days_to_keep_online=90):
    """
    Archive audit logs older than 90 days to compressed JSON
    Keep in database for 6 years per HIPAA requirement
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep_online)
    
    # Query old logs
    old_logs = AuditLog.query.filter(
        AuditLog.timestamp < cutoff_date
    ).all()
    
    if not old_logs:
        print("No logs to archive")
        return
    
    # Create archive file
    archive_filename = f"audit_logs_{cutoff_date.strftime('%Y%m%d')}.json.gz"
    archive_path = f"/mnt/compliance_archives/{archive_filename}"
    
    with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
        log_data = [log.to_dict() for log in old_logs]
        json.dump(log_data, f, indent=2)
    
    print(f"✅ Archived {len(old_logs)} logs to {archive_path}")
    
    # Upload to S3 for redundancy
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(
        archive_path,
        'alphawolf-compliance-archives',
        archive_filename,
        ExtraArgs={'ServerSideEncryption': 'aws:kms'}
    )
    
    print(f"✅ Uploaded archive to S3")
    
    # Mark logs as archived (don't delete from DB per HIPAA 6-year requirement)
    for log in old_logs:
        log.archived = True
    db.session.commit()
    
    print("✅ Marked logs as archived in database")

# Run via cron: 0 2 * * 0 (Every Sunday at 2 AM)
if __name__ == '__main__':
    archive_old_logs()
```

---

## 🔒 4. TRANSMISSION SECURITY (TLS)

### 4.1 Force HTTPS in Production

**Use Flask-Talisman:**
```bash
pip install flask-talisman
```

```python
# File: app.py

from flask_talisman import Talisman

if not app.debug:
    Talisman(app,
             force_https=True,
             force_https_permanent=True,
             strict_transport_security=True,
             strict_transport_security_max_age=31536000,  # 1 year
             strict_transport_security_include_subdomains=True,
             content_security_policy={
                 'default-src': ["'self'"],
                 'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
                 'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com'],
                 'font-src': ["'self'", 'fonts.gstatic.com'],
                 'img-src': ["'self'", 'data:', 'https:'],
                 'connect-src': ["'self'"],
                 'frame-ancestors': ["'none'"]
             },
             content_security_policy_nonce_in=['script-src'],
             feature_policy={
                 'geolocation': "'self'",
                 'camera': "'self'",
                 'microphone': "'self'"
             })
```

### 4.2 AWS Application Load Balancer (ALB) TLS Configuration

**Terraform configuration for ALB with TLS 1.3:**
```hcl
# File: infrastructure/alb.tf

resource "aws_lb" "alphawolf" {
  name               = "alphawolf-production-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true
  enable_http2              = true

  tags = {
    Name        = "AlphaWolf Production ALB"
    Environment = "production"
    Compliance  = "HIPAA"
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alphawolf.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"  # TLS 1.3 only
  certificate_arn   = aws_acm_certificate.alphawolf.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alphawolf.arn
  }
}

# Redirect HTTP to HTTPS
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.alphawolf.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

---

## 🧪 5. TESTING & VALIDATION

### 5.1 Encryption Testing

```python
# File: tests/test_encryption.py

import pytest
from services.encryption_service import PHIEncryptionService

def test_encryption_decryption():
    """Test basic encryption and decryption"""
    phi = PHIEncryptionService()
    
    plaintext = "Patient Name: John Doe, SSN: 123-45-6789"
    encrypted = phi.encrypt(plaintext)
    decrypted = phi.decrypt(encrypted)
    
    assert decrypted == plaintext
    assert encrypted != plaintext
    assert len(encrypted) > len(plaintext)

def test_encrypted_fields_in_database():
    """Test that PHI fields are encrypted in database"""
    user = User(
        username='testpatient',
        email='test@example.com',
        full_name='John Doe',
        ssn='123-45-6789'
    )
    db.session.add(user)
    db.session.commit()
    
    # Query raw database value
    result = db.session.execute(
        "SELECT full_name, ssn FROM users WHERE username='testpatient'"
    ).fetchone()
    
    # Raw values should be encrypted (Fernet format)
    assert result[0].startswith('gAAAAA')  # Fernet prefix
    assert result[1].startswith('gAAAAA')
    
    # But model properties should be decrypted
    assert user.full_name == 'John Doe'
    assert user.ssn == '123-45-6789'
```

### 5.2 Access Control Testing

```python
# File: tests/test_access_control.py

def test_patient_can_access_own_data(client, patient_user):
    """Test that patients can access their own PHI"""
    response = client.get(
        f'/api/patient/{patient_user.id}/medical-history',
        headers={'Authorization': f'Bearer {patient_user.token}'}
    )
    assert response.status_code == 200

def test_patient_cannot_access_others_data(client, patient_user, other_patient):
    """Test that patients cannot access other patients' PHI"""
    response = client.get(
        f'/api/patient/{other_patient.id}/medical-history',
        headers={'Authorization': f'Bearer {patient_user.token}'}
    )
    assert response.status_code == 403

def test_caregiver_can_access_assigned_patient(client, caregiver_user, assigned_patient):
    """Test that caregivers can access assigned patients' PHI"""
    response = client.get(
        f'/api/patient/{assigned_patient.id}/medical-history',
        headers={'Authorization': f'Bearer {caregiver_user.token}'}
    )
    assert response.status_code == 200

def test_mfa_required_for_admin(client, admin_user):
    """Test that admin accounts require MFA"""
    # Login without MFA token
    response = client.post('/api/auth/login', json={
        'username': admin_user.username,
        'password': 'correct_password'
    })
    assert response.json['mfa_required'] is True
```

### 5.3 Audit Logging Testing

```python
# File: tests/test_audit_logging.py

def test_phi_access_creates_audit_log(client, patient_user):
    """Test that PHI access is logged"""
    initial_log_count = AuditLog.query.count()
    
    response = client.get(
        f'/api/patient/{patient_user.id}/medical-history',
        headers={'Authorization': f'Bearer {patient_user.token}'}
    )
    
    final_log_count = AuditLog.query.count()
    assert final_log_count == initial_log_count + 1
    
    # Verify log content
    log = AuditLog.query.order_by(AuditLog.id.desc()).first()
    assert log.event_type == 'PHI_ACCESS'
    assert log.user_id == patient_user.id
    assert log.patient_id == patient_user.id
    assert log.action == 'GET'
    assert log.outcome == 'SUCCESS'

def test_failed_access_logged(client, patient_user, other_patient):
    """Test that failed PHI access attempts are logged"""
    response = client.get(
        f'/api/patient/{other_patient.id}/medical-history',
        headers={'Authorization': f'Bearer {patient_user.token}'}
    )
    
    log = AuditLog.query.order_by(AuditLog.id.desc()).first()
    assert log.outcome == 'DENIED'
```

---

## 🚀 6. DEPLOYMENT CHECKLIST

### Pre-Production

- [ ] All PHI fields encrypted in database
- [ ] Encryption keys stored in AWS KMS (not environment variables)
- [ ] TLS 1.3 enabled on load balancer
- [ ] MFA enabled for all administrative accounts
- [ ] RBAC implemented and tested
- [ ] Audit logging functional
- [ ] Session timeout configured (15 minutes)
- [ ] Automatic logout implemented
- [ ] Security headers configured (Talisman)
- [ ] Database encryption at rest enabled (RDS)
- [ ] Backup encryption enabled
- [ ] VPC security groups configured (least privilege)

### Post-Deployment

- [ ] Penetration testing completed
- [ ] Vulnerability scan passed
- [ ] Access control testing passed
- [ ] Audit log review (first 7 days)
- [ ] Performance testing under load
- [ ] Disaster recovery drill
- [ ] Backup restoration test
- [ ] Incident response drill

### Documentation

- [ ] HIPAA_COMPLIANCE_FRAMEWORK.md complete
- [ ] HIPAA_TECHNICAL_IMPLEMENTATION.md complete (this document)
- [ ] BAA templates prepared
- [ ] Notice of Privacy Practices published
- [ ] Security policies documented
- [ ] Incident response procedures documented
- [ ] Training materials prepared

---

## 📞 SUPPORT

**Technical Questions:**
Derek C. Junior (AI COO)
derek@thechristmanaiproject.com

**Compliance Questions:**
Everett N. Christman (Compliance Officer)
lumacognify@thechristmanaiproject.com

**Security Incidents:**
🚨 1-800-XXX-XXXX (24/7 Hotline)
security@thechristmanaiproject.com

---

© 2025 The Christman AI Project. All rights reserved.
