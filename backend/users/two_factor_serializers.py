from rest_framework import serializers
from .two_factor_models import TwoFactorAuth, TwoFactorAuditLog


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup"""
    secret_key = serializers.CharField(read_only=True)
    qr_code = serializers.CharField(read_only=True)
    setup_uri = serializers.CharField(read_only=True)
    backup_tokens = serializers.ListField(read_only=True)


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for 2FA token verification"""
    token = serializers.CharField(
        max_length=8, 
        min_length=6,
        help_text="6-digit TOTP code or 8-character backup token"
    )
    
    def validate_token(self, value):
        """Validate token format"""
        if not value.isdigit() and len(value) == 6:
            # TOTP token should be 6 digits
            pass
        elif not value.isalnum() and len(value) == 8:
            # Backup token should be 8 alphanumeric characters
            pass
        else:
            raise serializers.ValidationError(
                "Token must be either 6 digits or 8 alphanumeric characters"
            )
        return value


class TwoFactorLoginSerializer(serializers.Serializer):
    """Serializer for 2FA login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token_2fa = serializers.CharField(max_length=8, required=False)
    session_token = serializers.CharField(max_length=64, required=False)


class TwoFactorStatusSerializer(serializers.ModelSerializer):
    """Serializer for 2FA status"""
    backup_tokens_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TwoFactorAuth
        fields = [
            'is_enabled', 'setup_completed_at', 'last_used_at',
            'backup_tokens_count', 'recovery_email', 'recovery_phone'
        ]
        read_only_fields = ['setup_completed_at', 'last_used_at']
    
    def get_backup_tokens_count(self, obj):
        """Get count of remaining backup tokens"""
        return len(obj.backup_tokens)


class TwoFactorAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for 2FA audit logs"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = TwoFactorAuditLog
        fields = [
            'id', 'user_email', 'action', 'ip_address', 
            'user_agent', 'details', 'timestamp'
        ]
        read_only_fields = '__all__'


class BackupTokensSerializer(serializers.Serializer):
    """Serializer for backup tokens operations"""
    token = serializers.CharField(
        max_length=8,
        help_text="Current 2FA token required for security"
    )
    backup_tokens = serializers.ListField(read_only=True)


class TwoFactorRecoverySerializer(serializers.Serializer):
    """Serializer for 2FA account recovery"""
    email = serializers.EmailField()
    recovery_method = serializers.ChoiceField(
        choices=[('email', 'Email'), ('phone', 'Phone')],
        default='email'
    )


class TwoFactorSettingsSerializer(serializers.ModelSerializer):
    """Serializer for updating 2FA settings"""
    
    class Meta:
        model = TwoFactorAuth
        fields = ['recovery_email', 'recovery_phone']
    
    def validate_recovery_email(self, value):
        """Validate recovery email"""
        if value and value == self.instance.user.email:
            raise serializers.ValidationError(
                "Recovery email must be different from account email"
            )
        return value
