
# profiles/models.py
import uuid
from typing import TypeVar
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.exceptions import ValidationError

from django.contrib.gis.db import models as gis_models

from seasons.models import CropSeason,FieldAssignment


UserType = TypeVar("UserType", bound="User")

# enums
class PaymentInterval(models.TextChoices):
    # DAILY = "daily"
    # WEEKLY = "weekly"
    BIMONTHLY = "bimonthly"
    MONTHLY = "monthly"
    # YEARLY = "yearly"


class UserRole(models.TextChoices):
    EMPLOYEE = "employee"
    CUSTOMER = "customer"
    ADMIN = "admin"


class UserStatus(models.TextChoices):
    INACTIVE = "inactive"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    SUSPENDED = "suspended"


class TimeStampedModel(models.Model):
    '''__str__(self):
        return self.name
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    """
    Manager for AbstractUser-based User model. Username is preferred, but email/phone are accepted.
    """
    use_in_migrations = True

    def create_user(self, username: str, email: str = None, password: str = None, **extra_fields) -> UserType:
        if not username:
            raise ValueError("The username must be set")
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)  # type: ignore
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str = None, password: str = None, **extra_fields) -> UserType:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("status", "active")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model extending AbstractUser with role/status and optional email/phone identifiers.
    Login will still work with multiple identifiers via an auth backend.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coordinator', 'Coordinator'),
        # fields agent
        ('field_agent', 'Field Agent'),
    ]
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('deactivated', 'Deactivated'),
    ]
    TOKEN_CONTEXT = [
        ('activation', 'Account Activation'),
        ('password_reset', 'Password Reset'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # memorable predictable code(like say mMDF001f for farmer,MDF001e for employee,MDF001c for customer)
    phone_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(blank=False, null=False, unique=True)
    profile_image = models.FileField(upload_to="profiles/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    email_verified = models.BooleanField(default=False)
    token = models.UUIDField(choices=TOKEN_CONTEXT, blank=True, null=True, unique=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'
        # index some fields
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['phone_number']),
            models.Index(fields=["role", "username"]),
            # models.Index(fields=['token_expiry']),
        ]

    def save(self, *args, **kwargs):
        # if self.kra_pin:
        #     self.kra_pin = self.kra_pin.upper().strip()
        super().save(*args, **kwargs)

    def get_assigned_seasons(self):
        """Get all crop seasons assigned to this agent"""
        if self.role in ['admin', 'coordinator']:
            return CropSeason.objects.all()

        assigned_fields = FieldAssignment.objects.filter(user=self).values_list('field', flat=True)
        return CropSeason.objects.filter(field__in=assigned_fields)

    def can_manage_season(self, season):
        """Check if user can manage a specific season"""
        if self.role in ['admin', 'coordinator']:
            return True

        if self.role == 'field_agent':
            return FieldAssignment.objects.filter(
                user=self,
                field=season.field
            ).exists()

        return False


    def __str__(self):
        return self.username


class Field(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    boundary = gis_models.PolygonField(srid=4326)
    # add more fields as needed
    max_active_seasons = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class FieldAttachment(TimeStampedModel):
    """Attachments specific to fields (maps, boundary documents, ownership docs, etc.)"""

    ATTACHMENT_TYPES = [
        ('boundary_map', 'Boundary Map'),
        ('soil_report', 'Soil Report'),
        ('ownership_doc', 'Ownership Document'),
        ('field_photo', 'Field Photo'),
        ('other', 'Other'),
    ]

    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='fields/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='Size in bytes')
    mime_type = models.CharField(max_length=100)
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='other')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'field_attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field', 'attachment_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.filename}"

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name.split('/')[-1]
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

