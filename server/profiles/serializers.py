# profiles/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import Field, FieldAssignment, FieldAttachment, UserRole, UserStatus
from seasons.models import SeasonStatus
from seasons.serializers import CropSeasonDetailSerializer
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
        print(user)
        print(user.check_password(password))

        user = authenticate(username=user.email, password=password)
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


class FieldAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for field attachments"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    attachment_type_display = serializers.CharField(source='get_attachment_type_display', read_only=True)

    class Meta:
        model = FieldAttachment
        fields = [
            'id', 'field', 'file', 'filename', 'file_size', 'mime_type',
            'attachment_type', 'attachment_type_display', 'description',
            'uploaded_by', 'uploaded_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'filename', 'file_size', 'mime_type', 'created_at', 'updated_at']

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None


class FieldListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    active_season_count = serializers.IntegerField(read_only=True)
    assigned_agent_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'description', 'active_season_count',
            'assigned_agent_count', 'max_active_seasons',
            'created_at', 'updated_at'
        ]


class AssignedAgentSerializer(serializers.ModelSerializer):
    """Minimal agent info for field assignments"""
    agent_id = serializers.UUIDField(source='agent.id', read_only=True)
    agent_username = serializers.CharField(source='agent.username', read_only=True)
    agent_email = serializers.EmailField(source='agent.email', read_only=True)
    agent_phone = serializers.CharField(source='agent.phone_number', read_only=True)
    agent_status = serializers.CharField(source='agent.status', read_only=True)
    assigned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FieldAssignment
        fields = [
            'id', 'agent_id', 'agent_username', 'agent_email',
            'agent_phone', 'agent_status', 'assigned_by_name',
            'assigned_at'
        ]

    def get_assigned_by_name(self, obj):
        if obj.assigned_by:
            return obj.assigned_by.username
        return None



class FieldDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with active seasons, attachments, and assigned agents"""
    active_seasons = serializers.SerializerMethodField()
    attachments = FieldAttachmentSerializer(many=True, read_only=True)
    assigned_agents = serializers.SerializerMethodField()
    all_seasons_count = serializers.SerializerMethodField()
    completed_seasons_count = serializers.SerializerMethodField()

    active_season_count = serializers.IntegerField(read_only=True)
    # assigned_agent_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'description', 'max_active_seasons',
            'active_seasons', 'attachments', 'assigned_agents',
            'all_seasons_count', 'completed_seasons_count',
            'active_season_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_active_seasons(self, obj):
        """Get only active seasons for this field"""
        active_seasons = obj.seasons.filter(
            status=SeasonStatus.ACTIVE
        ).select_related('crop_type', 'created_by').order_by('-planting_date')

        return CropSeasonDetailSerializer(active_seasons, many=True).data

    def get_assigned_agents(self, obj):
        """Get all agents currently assigned to this field"""
        assignments = FieldAssignment.objects.filter(
            field=obj
        ).select_related('agent', 'assigned_by').order_by('-assigned_at')

        return AssignedAgentSerializer(assignments, many=True).data

    def get_all_seasons_count(self, obj):
        """Total number of seasons (all statuses)"""
        return obj.seasons.count()

    def get_completed_seasons_count(self, obj):
        """Number of completed seasons"""
        return obj.seasons.filter(status=SeasonStatus.COMPLETED).count()

    def get_active_season_count(self, obj):
        """Number of active seasons"""
        return obj.seasons.filter(status=SeasonStatus.ACTIVE).count()


class FieldSerializer(serializers.ModelSerializer):
    """
    Main field serializer that uses different serializers based on context.
    Write operations use base fields only.
    Read operations differentiate between list and detail views.
    """

    class Meta:
        model = Field
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Use different serializers for list vs detail views
        """
        request = self.context.get('request')

        # Detail view (single object retrieval)
        if request and request.method == 'GET' and not self.parent:
            # Check if it's a detail view (has pk in URL)
            view = self.context.get('view')
            if view and view.action == 'retrieve':
                return FieldDetailSerializer(instance, context=self.context).data

        # List view or other cases
        if request and hasattr(request, 'parser_context'):
            return FieldListSerializer(instance, context=self.context).data

        return super().to_representation(instance)

    def validate_name(self, value):
        """Ensure field name is unique (case-insensitive)"""
        if Field.objects.filter(name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A field with this name already exists.")
        return value

    def validate_max_active_seasons(self, value):
        """Ensure max_active_seasons is at least 1"""
        if value < 1:
            raise serializers.ValidationError("Must allow at least one active season.")
        return value

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




class BulkFieldAssignmentSerializer(serializers.Serializer):
    """Bulk assignment serializer"""
    field_id = serializers.UUIDField()
    agent_ids = serializers.ListField(child=serializers.UUIDField())
