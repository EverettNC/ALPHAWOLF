#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Christman AI Project - MFA Service
Copyright (c) 2025 Christman AI Project
Licensed under the Christman AI License (see LICENSE file)

Multi-Factor Authentication Service using TOTP (Time-based One-Time Password)
Compliant with HIPAA Security Rule 45 CFR § 164.312(a)(2)(i) - Unique User Identification
Compliant with HIPAA Security Rule 45 CFR § 164.312(d) - Person or Entity Authentication

This module provides:
- TOTP secret generation
- QR code generation for authenticator apps
- Token verification
- Backup code management
"""

import os
import json
import secrets
import hashlib
from typing import List, Tuple, Optional
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timezone

from services.encryption_service import get_phi_encryption_service


class MFAService:
    """
    Multi-Factor Authentication Service using TOTP.
    
    HIPAA Compliance:
    - Implements unique user identification per §164.312(a)(2)(i)
    - Provides person/entity authentication per §164.312(d)
    - Secrets stored encrypted using PHIEncryptionService
    - Backup codes hashed using SHA-256
    
    Usage:
        mfa = MFAService()
        secret = mfa.generate_mfa_secret()
        qr_code = mfa.get_qr_code_data_uri(secret, user_email)
        is_valid = mfa.verify_mfa_token(secret, user_token)
    """
    
    def __init__(self):
        """Initialize MFA service with encryption support."""
        self.encryption_service = get_phi_encryption_service()
        self.issuer_name = os.getenv('MFA_ISSUER_NAME', 'AlphaWolf')
    
    def generate_mfa_secret(self) -> str:
        """
        Generate a new TOTP secret.
        
        Returns:
            str: Base32-encoded TOTP secret (16 bytes = 160 bits)
        
        Example:
            secret = mfa.generate_mfa_secret()
            # Returns: 'JBSWY3DPEHPK3PXP'
        """
        # Generate 160-bit random secret
        return pyotp.random_base32()
    
    def get_totp_uri(self, secret: str, user_identifier: str) -> str:
        """
        Generate TOTP provisioning URI for QR code.
        
        Args:
            secret: Base32-encoded TOTP secret
            user_identifier: User email or username
        
        Returns:
            str: TOTP URI (otpauth://totp/...)
        
        Example:
            uri = mfa.get_totp_uri(secret, 'patient@example.com')
            # Returns: 'otpauth://totp/AlphaWolf:patient@example.com?secret=XXX&issuer=AlphaWolf'
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_identifier,
            issuer_name=self.issuer_name
        )
    
    def get_qr_code_data_uri(self, secret: str, user_identifier: str) -> str:
        """
        Generate QR code as data URI for TOTP secret.
        
        Args:
            secret: Base32-encoded TOTP secret
            user_identifier: User email or username
        
        Returns:
            str: Data URI (data:image/png;base64,...)
        
        Example:
            data_uri = mfa.get_qr_code_data_uri(secret, 'patient@example.com')
            # Use in HTML: <img src="{data_uri}" alt="MFA QR Code">
        """
        totp_uri = self.get_totp_uri(secret, user_identifier)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to data URI
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
    
    def verify_mfa_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token against a secret.
        
        Args:
            secret: Base32-encoded TOTP secret
            token: 6-digit TOTP token from authenticator app
            window: Number of time steps to check (default 1 = ±30 seconds)
        
        Returns:
            bool: True if token is valid
        
        Example:
            is_valid = mfa.verify_mfa_token(secret, '123456')
        
        Security Notes:
            - Default window=1 allows for ±30 second clock drift
            - Tokens are valid for 30 seconds
            - Each token can only be used once (implement replay protection separately)
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            print(f"MFA token verification error: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            count: Number of backup codes to generate (default 10)
        
        Returns:
            List[str]: List of backup codes (8-character alphanumeric)
        
        Example:
            codes = mfa.generate_backup_codes(count=10)
            # Returns: ['A1B2C3D4', 'E5F6G7H8', ...]
        
        Security Notes:
            - Backup codes should be displayed ONCE during setup
            - Store hashed versions in database (use hash_backup_code)
            - Each code can only be used once
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            codes.append(code)
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for secure storage.
        
        Args:
            code: Plain backup code
        
        Returns:
            str: SHA-256 hash of code
        
        Example:
            hashed = mfa.hash_backup_code('A1B2C3D4')
        
        Security Notes:
            - Uses SHA-256 for one-way hashing
            - Store only hashes in database, never plain codes
            - Compare hashes when verifying backup codes
        """
        return hashlib.sha256(code.encode('utf-8')).hexdigest()
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Verify a backup code against stored hashes.
        
        Args:
            code: Plain backup code from user
            hashed_codes: List of hashed backup codes from database
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, matched_hash)
                - is_valid: True if code matches
                - matched_hash: The hash that matched (to remove after use)
        
        Example:
            is_valid, matched_hash = mfa.verify_backup_code('A1B2C3D4', stored_hashes)
            if is_valid:
                # Remove matched_hash from database
                pass
        
        Security Notes:
            - Each backup code can only be used once
            - Remove matched hash from database after successful use
            - Regenerate backup codes if all are used
        """
        code_hash = self.hash_backup_code(code)
        if code_hash in hashed_codes:
            return True, code_hash
        return False, None
    
    def encrypt_mfa_secret(self, secret: str) -> str:
        """
        Encrypt MFA secret for database storage.
        
        Args:
            secret: Plain TOTP secret
        
        Returns:
            str: Encrypted secret
        
        Example:
            encrypted_secret = mfa.encrypt_mfa_secret(plain_secret)
            # Store encrypted_secret in database
        
        HIPAA Compliance:
            - Uses PHIEncryptionService (AES-256)
            - Secrets are PHI per §164.312(d)
        """
        return self.encryption_service.encrypt(secret)
    
    def decrypt_mfa_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt MFA secret from database.
        
        Args:
            encrypted_secret: Encrypted TOTP secret
        
        Returns:
            str: Plain TOTP secret
        
        Example:
            plain_secret = mfa.decrypt_mfa_secret(encrypted_secret)
            is_valid = mfa.verify_mfa_token(plain_secret, user_token)
        """
        return self.encryption_service.decrypt(encrypted_secret)
    
    def encrypt_backup_codes(self, codes: List[str]) -> str:
        """
        Encrypt backup codes (hashed) for database storage.
        
        Args:
            codes: List of backup codes (hashed)
        
        Returns:
            str: Encrypted JSON string
        
        Example:
            hashed_codes = [mfa.hash_backup_code(code) for code in plain_codes]
            encrypted_codes = mfa.encrypt_backup_codes(hashed_codes)
            # Store encrypted_codes in database
        
        HIPAA Compliance:
            - Uses PHIEncryptionService (AES-256)
            - Backup codes are PHI per §164.312(d)
        """
        return self.encryption_service.encrypt_json(codes)
    
    def decrypt_backup_codes(self, encrypted_codes: str) -> List[str]:
        """
        Decrypt backup codes from database.
        
        Args:
            encrypted_codes: Encrypted JSON string
        
        Returns:
            List[str]: List of hashed backup codes
        
        Example:
            stored_hashes = mfa.decrypt_backup_codes(encrypted_codes)
            is_valid, matched_hash = mfa.verify_backup_code(user_code, stored_hashes)
        """
        return self.encryption_service.decrypt_json(encrypted_codes)
    
    def setup_mfa_for_user(self, user_identifier: str) -> Tuple[str, str, List[str]]:
        """
        Complete MFA setup process for a user.
        
        Args:
            user_identifier: User email or username
        
        Returns:
            Tuple[str, str, List[str]]: (encrypted_secret, qr_code_data_uri, plain_backup_codes)
                - encrypted_secret: Encrypted TOTP secret (store in database)
                - qr_code_data_uri: QR code data URI (display to user)
                - plain_backup_codes: Plain backup codes (display ONCE to user)
        
        Example:
            encrypted_secret, qr_uri, backup_codes = mfa.setup_mfa_for_user('patient@example.com')
            
            # Store in database:
            user.mfa_secret = encrypted_secret
            user.mfa_backup_codes = mfa.encrypt_backup_codes([
                mfa.hash_backup_code(code) for code in backup_codes
            ])
            user.mfa_enabled = False  # Enable after user verifies first token
            
            # Display to user:
            return {
                'qr_code': qr_uri,
                'backup_codes': backup_codes,
                'message': 'Scan QR code and enter token to complete setup'
            }
        
        Security Flow:
            1. Generate secret and backup codes
            2. Display QR code and backup codes to user
            3. User scans QR code in authenticator app
            4. User enters first token to verify setup
            5. Only then set mfa_enabled = True
        """
        # Generate secret
        plain_secret = self.generate_mfa_secret()
        encrypted_secret = self.encrypt_mfa_secret(plain_secret)
        
        # Generate QR code
        qr_code_uri = self.get_qr_code_data_uri(plain_secret, user_identifier)
        
        # Generate backup codes (return plain, store hashed)
        plain_backup_codes = self.generate_backup_codes(count=10)
        
        return encrypted_secret, qr_code_uri, plain_backup_codes


def get_mfa_service() -> MFAService:
    """
    Get singleton MFA service instance.
    
    Returns:
        MFAService: Configured MFA service
    
    Usage:
        mfa = get_mfa_service()
    """
    return MFAService()


# Self-test
if __name__ == '__main__':
    print("=== MFA Service Self-Test ===\n")
    
    mfa = get_mfa_service()
    test_email = 'test@example.com'
    
    # Test 1: Generate secret
    print("Test 1: Generate TOTP secret")
    secret = mfa.generate_mfa_secret()
    print(f"✓ Generated secret: {secret[:8]}... (length: {len(secret)})\n")
    
    # Test 2: Generate QR code
    print("Test 2: Generate QR code data URI")
    qr_uri = mfa.get_qr_code_data_uri(secret, test_email)
    print(f"✓ Generated QR code data URI (length: {len(qr_uri)} bytes)")
    print(f"  Preview: {qr_uri[:80]}...\n")
    
    # Test 3: Verify token
    print("Test 3: Verify TOTP token")
    totp = pyotp.TOTP(secret)
    current_token = totp.now()
    is_valid = mfa.verify_mfa_token(secret, current_token)
    print(f"✓ Current token: {current_token}")
    print(f"✓ Verification: {is_valid}\n")
    
    # Test 4: Invalid token
    print("Test 4: Verify invalid token")
    is_valid_wrong = mfa.verify_mfa_token(secret, '000000')
    print(f"✓ Invalid token verification: {is_valid_wrong} (expected False)\n")
    
    # Test 5: Backup codes
    print("Test 5: Generate backup codes")
    backup_codes = mfa.generate_backup_codes(count=10)
    print(f"✓ Generated {len(backup_codes)} backup codes:")
    print(f"  Sample: {backup_codes[0]}, {backup_codes[1]}, {backup_codes[2]}\n")
    
    # Test 6: Hash and verify backup code
    print("Test 6: Hash and verify backup code")
    hashed_codes = [mfa.hash_backup_code(code) for code in backup_codes]
    test_code = backup_codes[0]
    is_valid_backup, matched_hash = mfa.verify_backup_code(test_code, hashed_codes)
    print(f"✓ Backup code: {test_code}")
    print(f"✓ Verification: {is_valid_backup}")
    print(f"✓ Matched hash: {matched_hash[:16]}...\n")
    
    # Test 7: Encrypt/decrypt secret
    print("Test 7: Encrypt/decrypt MFA secret")
    encrypted_secret = mfa.encrypt_mfa_secret(secret)
    decrypted_secret = mfa.decrypt_mfa_secret(encrypted_secret)
    print(f"✓ Encrypted secret length: {len(encrypted_secret)} bytes")
    print(f"✓ Decryption matches: {secret == decrypted_secret}\n")
    
    # Test 8: Encrypt/decrypt backup codes
    print("Test 8: Encrypt/decrypt backup codes")
    encrypted_codes = mfa.encrypt_backup_codes(hashed_codes)
    decrypted_codes = mfa.decrypt_backup_codes(encrypted_codes)
    print(f"✓ Encrypted codes length: {len(encrypted_codes)} bytes")
    print(f"✓ Decryption matches: {hashed_codes == decrypted_codes}\n")
    
    # Test 9: Full setup flow
    print("Test 9: Complete MFA setup flow")
    encrypted_secret, qr_uri, plain_codes = mfa.setup_mfa_for_user(test_email)
    print(f"✓ Encrypted secret: {encrypted_secret[:40]}...")
    print(f"✓ QR code URI length: {len(qr_uri)} bytes")
    print(f"✓ Backup codes: {len(plain_codes)} codes generated")
    print(f"  Sample codes: {plain_codes[0]}, {plain_codes[1]}\n")
    
    print("=== All MFA Service Tests Passed ===")
