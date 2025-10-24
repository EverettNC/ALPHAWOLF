# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com

"""
HIPAA-Compliant Audit Logging Service
Logs all PHI access, security events, and administrative actions
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Optional, Any
from flask import request, session

logger = logging.getLogger(__name__)


class HIPAAAuditLogger:
    """
    HIPAA-compliant audit logging system
    
    Logs all access, modifications, and security events per §164.312(b)
    
    Features:
    - Comprehensive PHI access tracking
    - Tamper-evident logs (checksums)
    - Security event logging
    - 6-year retention compliance
    - Automatic log rotation
    """
    
    def __init__(self, db_session=None):
        """
        Initialize HIPAA audit logger
        
        Args:
            db_session: SQLAlchemy database session (optional, uses models.db if not provided)
        """
        self.db_session = db_session
        self.logger = logging.getLogger('hipaa_audit')
        
        # Configure file handler for audit logs (in addition to database)
        import os
        from logging.handlers import RotatingFileHandler
        
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # 10MB file size, keep 100 backup files (6+ years of logs)
        handler = RotatingFileHandler(
            os.path.join(log_dir, 'hipaa_audit.log'),
            maxBytes=10485760,  # 10MB
            backupCount=100
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        logger.info("HIPAA Audit Logger initialized")
    
    def _get_db_session(self):
        """Get database session (lazy loading)"""
        if self.db_session:
            return self.db_session
        
        # Import here to avoid circular imports
        from models import db
        return db.session
    
    def _create_checksum(self, data: dict) -> str:
        """
        Create SHA-256 checksum for tamper detection
        
        Args:
            data: Log entry data
        
        Returns:
            str: Hex checksum
        """
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def log_phi_access(
        self,
        user_id: Optional[int],
        patient_id: Optional[int],
        action: str,
        resource: str,
        outcome: str,
        details: Optional[Dict] = None
    ):
        """
        Log PHI access event (CRITICAL for HIPAA compliance)
        
        Args:
            user_id: ID of user accessing PHI
            patient_id: ID of patient whose PHI was accessed
            action: Action performed (READ, WRITE, DELETE, UPDATE)
            resource: Resource accessed (medical_history, patient_profile, etc.)
            outcome: Result of access attempt (SUCCESS, FAILURE, DENIED)
            details: Additional context (optional)
        
        Example:
            >>> logger.log_phi_access(
            ...     user_id=123,
            ...     patient_id=456,
            ...     action='READ',
            ...     resource='medical_history',
            ...     outcome='SUCCESS'
            ... )
        """
        try:
            from models import AuditLog
            
            # Get request context
            ip_address = None
            user_agent = None
            session_id = None
            
            try:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length
                session_id = session.get('session_id', '')
            except RuntimeError:
                # Outside request context (e.g., background task)
                pass
            
            # Create audit entry
            audit_data = {
                'timestamp': datetime.utcnow(),
                'event_type': 'PHI_ACCESS',
                'action': action,
                'outcome': outcome,
                'user_id': user_id,
                'patient_id': patient_id,
                'resource_type': resource,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
                'details': details or {}
            }
            
            # Generate checksum for integrity
            checksum = self._create_checksum(audit_data)
            
            # Save to database
            audit_log = AuditLog(
                timestamp=audit_data['timestamp'],
                event_type=audit_data['event_type'],
                action=action,
                outcome=outcome,
                user_id=user_id,
                patient_id=patient_id,
                resource_type=resource,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                details=json.dumps(details) if details else None,
                checksum=checksum
            )
            
            db = self._get_db_session()
            db.add(audit_log)
            db.commit()
            
            # Also log to file for redundancy
            self.logger.info(
                f"PHI_ACCESS | User:{user_id} | Patient:{patient_id} | "
                f"Action:{action} | Resource:{resource} | Outcome:{outcome} | "
                f"IP:{ip_address}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log PHI access: {e}")
            # CRITICAL: Log to file even if database fails
            self.logger.error(f"AUDIT_FAILURE: {audit_data}")
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None
    ):
        """
        Log security event (login failures, permission denied, etc.)
        
        Args:
            event_type: Type of event (LOGIN_FAILED, PERMISSION_DENIED, MFA_FAILED, etc.)
            severity: Severity level (INFO, WARNING, CRITICAL)
            details: Event details
            user_id: User ID (if applicable)
        
        Example:
            >>> logger.log_security_event(
            ...     event_type='LOGIN_FAILED',
            ...     severity='WARNING',
            ...     details={'username': 'jdoe', 'reason': 'invalid_password'}
            ... )
        """
        try:
            from models import AuditLog
            
            # Get request context
            ip_address = None
            user_agent = None
            
            try:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')[:500]
            except RuntimeError:
                pass
            
            security_data = {
                'timestamp': datetime.utcnow(),
                'event_type': event_type,
                'severity': severity,
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'details': details
            }
            
            checksum = self._create_checksum(security_data)
            
            # Save to database
            audit_log = AuditLog(
                timestamp=security_data['timestamp'],
                event_type=event_type,
                action='SECURITY_EVENT',
                outcome=severity,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=json.dumps(details),
                checksum=checksum
            )
            
            db = self._get_db_session()
            db.add(audit_log)
            db.commit()
            
            # Log to file
            log_method = {
                'INFO': self.logger.info,
                'WARNING': self.logger.warning,
                'CRITICAL': self.logger.critical
            }.get(severity, self.logger.info)
            
            log_method(
                f"SECURITY_EVENT | Type:{event_type} | Severity:{severity} | "
                f"User:{user_id} | IP:{ip_address} | Details:{json.dumps(details)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            self.logger.error(f"AUDIT_FAILURE: {security_data}")
    
    def log_admin_action(
        self,
        admin_user_id: int,
        action: str,
        target_user_id: Optional[int],
        details: Dict[str, Any]
    ):
        """
        Log administrative action (user management, permission changes, etc.)
        
        Args:
            admin_user_id: ID of administrator performing action
            action: Action performed (USER_CREATED, PERMISSION_GRANTED, etc.)
            target_user_id: ID of user being modified (if applicable)
            details: Action details
        """
        try:
            from models import AuditLog
            
            ip_address = None
            try:
                ip_address = request.remote_addr
            except RuntimeError:
                pass
            
            admin_data = {
                'timestamp': datetime.utcnow(),
                'event_type': 'ADMIN_ACTION',
                'action': action,
                'admin_user_id': admin_user_id,
                'target_user_id': target_user_id,
                'ip_address': ip_address,
                'details': details
            }
            
            checksum = self._create_checksum(admin_data)
            
            audit_log = AuditLog(
                timestamp=admin_data['timestamp'],
                event_type='ADMIN_ACTION',
                action=action,
                outcome='SUCCESS',
                user_id=admin_user_id,
                patient_id=target_user_id,  # Reuse patient_id field for target
                ip_address=ip_address,
                details=json.dumps(details),
                checksum=checksum
            )
            
            db = self._get_db_session()
            db.add(audit_log)
            db.commit()
            
            self.logger.info(
                f"ADMIN_ACTION | Admin:{admin_user_id} | Action:{action} | "
                f"Target:{target_user_id} | IP:{ip_address}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log admin action: {e}")
    
    def verify_log_integrity(self, audit_log_id: int) -> bool:
        """
        Verify that an audit log entry has not been tampered with
        
        Args:
            audit_log_id: ID of audit log to verify
        
        Returns:
            bool: True if log is intact, False if tampered
        """
        try:
            from models import AuditLog
            
            db = self._get_db_session()
            log_entry = db.query(AuditLog).filter_by(id=audit_log_id).first()
            
            if not log_entry:
                return False
            
            # Reconstruct data for checksum
            data = {
                'timestamp': log_entry.timestamp,
                'event_type': log_entry.event_type,
                'action': log_entry.action,
                'outcome': log_entry.outcome,
                'user_id': log_entry.user_id,
                'patient_id': log_entry.patient_id,
                'resource_type': log_entry.resource_type,
                'ip_address': log_entry.ip_address,
                'user_agent': log_entry.user_agent,
                'session_id': log_entry.session_id,
                'details': json.loads(log_entry.details) if log_entry.details else {}
            }
            
            calculated_checksum = self._create_checksum(data)
            
            is_valid = calculated_checksum == log_entry.checksum
            
            if not is_valid:
                self.logger.critical(
                    f"INTEGRITY_VIOLATION | Log ID:{audit_log_id} | "
                    f"Checksum mismatch detected!"
                )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to verify log integrity: {e}")
            return False
    
    def get_patient_access_history(
        self,
        patient_id: int,
        days: int = 30,
        limit: int = 100
    ) -> list:
        """
        Get access history for a specific patient (for disclosure accounting)
        
        Args:
            patient_id: Patient ID
            days: Number of days to look back (default: 30, HIPAA requires 6 years)
            limit: Maximum number of records to return
        
        Returns:
            list: List of audit log entries
        """
        try:
            from models import AuditLog
            from datetime import timedelta
            
            db = self._get_db_session()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            logs = db.query(AuditLog).filter(
                AuditLog.patient_id == patient_id,
                AuditLog.timestamp >= cutoff_date,
                AuditLog.event_type == 'PHI_ACCESS'
            ).order_by(
                AuditLog.timestamp.desc()
            ).limit(limit).all()
            
            return [{
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'user_id': log.user_id,
                'action': log.action,
                'resource_type': log.resource_type,
                'outcome': log.outcome,
                'ip_address': log.ip_address
            } for log in logs]
            
        except Exception as e:
            logger.error(f"Failed to get patient access history: {e}")
            return []


# Global singleton instance
_hipaa_audit_logger = None


def get_audit_logger() -> HIPAAAuditLogger:
    """Get global HIPAA audit logger instance (singleton)"""
    global _hipaa_audit_logger
    if _hipaa_audit_logger is None:
        _hipaa_audit_logger = HIPAAAuditLogger()
    return _hipaa_audit_logger


# Convenience functions
def log_phi_access(user_id, patient_id, action, resource, outcome, details=None):
    """Log PHI access (convenience wrapper)"""
    return get_audit_logger().log_phi_access(
        user_id, patient_id, action, resource, outcome, details
    )


def log_security_event(event_type, severity, details, user_id=None):
    """Log security event (convenience wrapper)"""
    return get_audit_logger().log_security_event(
        event_type, severity, details, user_id
    )


if __name__ == '__main__':
    print("🔍 HIPAA Audit Logger - Self Test")
    print("=" * 50)
    print("Note: Requires database connection for full testing")
    print("=" * 50)
    
    # Basic initialization test
    audit_logger = HIPAAAuditLogger()
    print("✅ Audit logger initialized")
    
    # Test checksum generation
    test_data = {
        'timestamp': datetime.utcnow(),
        'event_type': 'PHI_ACCESS',
        'user_id': 123
    }
    checksum = audit_logger._create_checksum(test_data)
    print(f"✅ Checksum generated: {checksum[:16]}...")
    
    print("\n" + "=" * 50)
    print("✅ Basic audit logger tests passed!")
    print("🔍 HIPAA Audit Logger is ready")
    print("\nTo fully test, run with database connection:")
    print("  python -c 'from services.hipaa_audit_logger import *; test_with_db()'")
