# profiles/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import Field, FieldAssignment, FieldAttachment, UserRole, UserStatus
from rest_framework.exceptions import AuthenticationFailed, ValidationError
# import Q
from django.db.models import Q

User = get_user_model()


# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     """Custom JWT serializer with additional user data"""
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"
    # def validate(self, attrs):
    #     data = super().validate(attrs)

    #     # Add extra response data
    #     data['user'] = {
    #         'id': str(self.user.id),
    #         'username': self.user.username,
    #         'email': self.user.email,
    #         'role': self.user.role,
    #         'status': self.user.status,
    #     }

    #     return data

class TokenLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier", "").strip()
        password = attrs.get("password")

        print(identifier)

        if not identifier or not password:
            raise serializers.ValidationError("Identifier and password are required.")

        normalized_identifier = identifier
        if "@" in identifier:
            normalized_identifier = identifier.lower()

        phone_identifier = "".join(ch for ch in identifier if ch.isdigit())

        try:
            user = User.objects.get(
                Q(email__iexact=normalized_identifier) |
                Q(phone_number__iexact=phone_identifier) |
                Q(username__iexact=identifier)
            )
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credential")
        except User.MultipleObjectsReturned:
            raise AuthenticationFailed("Multiple accounts found")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        attrs["user"] = user
        return attrs



class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password', 'password2', 'role')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """User model serializer"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone_number', 'profile_image',
            'role', 'status', 'email_verified', 'full_name',
            'first_name', 'last_name', 'is_active', 'date_joined',
            'last_login', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'email_verified', 'date_joined', 'last_login', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer (no password change)"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone_number', 'profile_image',
            'first_name', 'last_name', 'role', 'status'
        )
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value


class FieldSerializer(serializers.ModelSerializer):
    """Field model serializer"""
    assigned_agents_count = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = (
            'id', 'name', 'description', 'max_active_seasons',
            'assigned_agents_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_assigned_agents_count(self, obj):
        return obj.fieldassignment_set.count()


class FieldAssignmentSerializer(serializers.ModelSerializer):
    """Field assignment serializer"""
    agent_username = serializers.CharField(source='agent.username', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = FieldAssignment
        fields = (
            'id', 'field', 'field_name', 'agent', 'agent_username',
            'assigned_by', 'assigned_by_username', 'assigned_at'
        )
        read_only_fields = ('id', 'assigned_at', 'assigned_by')

    def validate(self, attrs):
        # Check for duplicate assignment
        if FieldAssignment.objects.filter(
            field=attrs['field'],
            agent=attrs['agent']
        ).exists():
            raise serializers.ValidationError("This agent is already assigned to this field.")
        return attrs


class FieldAttachmentSerializer(serializers.ModelSerializer):
    """Field attachment serializer"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = FieldAttachment
        fields = (
            'id', 'field', 'file', 'filename', 'file_size',
            'mime_type', 'attachment_type', 'description',
            'uploaded_by', 'uploaded_by_username', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'created_at', 'updated_at')


class BulkFieldAssignmentSerializer(serializers.Serializer):
    """Bulk assignment serializer"""
    field_id = serializers.UUIDField()
    agent_ids = serializers.ListField(child=serializers.UUIDField())
