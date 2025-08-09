from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
import string

User = get_user_model()


class TwoFactorAuth(models.Model):
    """Two-Factor Authentication settings for users"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='two_factor_auth'
    )
    
    # TOTP (Time-based One-Time Password) settings
    secret_key = models.CharField(max_length=32, blank=True)
    is_enabled = models.BooleanField(default=False)
    backup_tokens = models.JSONField(default=list, blank=True)
    
    # Setup tracking
    setup_completed_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Recovery options
    recovery_email = models.EmailField(blank=True)
    recovery_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"2FA for {self.user.email}"
    
    def generate_secret_key(self):
        """Generate a new secret key for TOTP"""
        self.secret_key = pyotp.random_base32()
        return self.secret_key
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code generation"""
        if not self.secret_key:
            self.generate_secret_key()
        
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name="SkillSphere"
        )
    
    def generate_qr_code(self):
        """Generate QR code for authenticator app setup"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for easy frontend consumption
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, token):
        """Verify TOTP token"""
        if not self.secret_key or not self.is_enabled:
            return False
        
        totp = pyotp.TOTP(self.secret_key)
        is_valid = totp.verify(token, valid_window=1)  # Allow 30 second window
        
        if is_valid:
            self.last_used_at = timezone.now()
            self.save(update_fields=['last_used_at'])
        
        return is_valid
    
    def generate_backup_tokens(self, count=10):
        """Generate backup recovery tokens"""
        tokens = []
        for _ in range(count):
            token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            tokens.append(token)
        
        self.backup_tokens = tokens
        self.save(update_fields=['backup_tokens'])
        return tokens
    
    def use_backup_token(self, token):
        """Use a backup token (one-time use)"""
        if token in self.backup_tokens:
            self.backup_tokens.remove(token)
            self.save(update_fields=['backup_tokens'])
            return True
        return False
    
    def disable_2fa(self):
        """Disable 2FA and clear sensitive data"""
        self.is_enabled = False
        self.secret_key = ''
        self.backup_tokens = []
        self.save()


class TwoFactorSession(models.Model):
    """Temporary session for 2FA verification process"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=64, unique=True)
    is_verified = models.BooleanField(default=False)
    verification_attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['user', 'is_verified']),
        ]
    
    def __str__(self):
        return f"2FA Session for {self.user.email}"
    
    def is_expired(self):
        """Check if session has expired"""
        return timezone.now() > self.expires_at
    
    def can_attempt(self):
        """Check if more verification attempts are allowed"""
        return self.verification_attempts < self.max_attempts and not self.is_expired()
    
    def record_attempt(self):
        """Record a verification attempt"""
        self.verification_attempts += 1
        self.save(update_fields=['verification_attempts'])
    
    def verify(self):
        """Mark session as verified"""
        self.is_verified = True
        self.save(update_fields=['is_verified'])


class TwoFactorAuditLog(models.Model):
    """Audit log for 2FA activities"""
    ACTION_CHOICES = [
        ('setup', 'Setup Started'),
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
        ('verified', 'Token Verified'),
        ('failed', 'Verification Failed'),
        ('backup_used', 'Backup Token Used'),
        ('backup_generated', 'Backup Tokens Generated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
