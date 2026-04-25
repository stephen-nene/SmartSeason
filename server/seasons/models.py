# seasons/models.py
from django.db import models
# from django.contrib.gis.db import models as gis_models

from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.



# class FieldUpdateStage(models.TextChoices):
#     PLANTED = "planted"
#     GROWING = "growing"
#     READY = "ready"
#     HARVESTED = "harvested"

#     PLANTING = "planting"
#     GERMINATION = "germination"
#     SEEDLING = "seedling"
#     VEGETATIVE = "vegetative"

#     FLOWERING = "flowering"
#     FRUITING = "fruiting"
#     HARVEST = "harvest"
#     DORMANT = "dormant"

class FieldUpdateStage(models.TextChoices):
    PLANTED = "planted"
    GROWING = "growing"
    READY = "ready"
    HARVESTED = "harvested"

class SeasonStatus(models.TextChoices):
    ACTIVE = "active"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    DEACTIVATED = "deactivated"
    INACTIVE = "inactive"

class TimeStampedModel(models.Model):
    '''__str__(self):
        return self.name
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CropType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    growth_cycle_days = models.IntegerField()

    def __str__(self):
        return self.name




class CropSeason(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    field  = models.ForeignKey('profiles.Field', related_name='seasons', on_delete=models.CASCADE)
    crop_type = models.ForeignKey(CropType, related_name='seasons', on_delete=models.CASCADE)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    actual_harvest_date = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=SeasonStatus.choices, default=SeasonStatus.ACTIVE)
    current_stage = models.CharField(max_length=50, choices=FieldUpdateStage.choices, default=FieldUpdateStage.PLANTED)

    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='seasons_created', on_delete=models.CASCADE)

    @property
    def computed_status(self):
        """Calculate season status based on planting date, expected harvest, and updates"""
        from django.utils import timezone
        today = timezone.now().date()

        # Completed
        if self.current_stage == FieldUpdateStage.HARVESTED or self.actual_harvest_date:
            return SeasonStatus.COMPLETED

        # At Risk
        if today > self.expected_harvest_date and self.current_stage != FieldUpdateStage.HARVESTED:
            return SeasonStatus.AT_RISK


        # Calculate days since planting
        days_since_planting = (today - self.planting_date).days

        # Check for delayed growth (no updates in last 7 days)
        last_update = self.fieldupdate_set.order_by('-created_at').first()
        if last_update and (today - last_update.created_at.date()).days > 7:
            if self.current_stage not in [FieldUpdateStage.READY, FieldUpdateStage.HARVESTED]:
                return SeasonStatus.AT_RISK

        # compare days since planting to growth cycle of crop
        total_cycle = self.crop_type.growth_cycle_days
        if days_since_planting > total_cycle:
            return SeasonStatus.AT_RISK

        # Active
        return SeasonStatus.ACTIVE


    def save(self, *args, **kwargs):
        # Don't call computed_status() as method if it's a property
        if not self.actual_harvest_date:
            self.status = self.computed_status  # Remove the ()
        super().save(*args, **kwargs)

    @property
    def days_since_planting(self):
        from django.utils import timezone
        return (timezone.now().date() - self.planting_date).days

    @property
    def progress_percentage(self):
        """Calculate crop progress based on expected harvest date"""
        from django.utils import timezone

        if self.actual_harvest_date:
            return 100

        total_days = (self.expected_harvest_date - self.planting_date).days
        elapsed_days = (timezone.now().date() - self.planting_date).days

        if elapsed_days >= total_days:
            return 100

        return min(int((elapsed_days / total_days) * 100), 100)

    def __str__(self):
        return self.name

    #  Enforce ONE active season per field
    class Meta:
        constraints = [
        models.UniqueConstraint(
    fields=["field"],
    condition=models.Q(status="active"),
    name="one_active_season_per_field"
)
        ]



class FieldUpdate(TimeStampedModel):
    crop_season = models.ForeignKey(CropSeason, on_delete=models.CASCADE)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='field_updates', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, choices=FieldUpdateStage.choices, null=False, blank=False)
    notes = models.TextField()

    def clean(self):
        super().clean()
        if self.crop_season and self.crop_season.status == SeasonStatus.COMPLETED:
            raise ValidationError("Cannot update a completed season")

    def save(self, *args, **kwargs):
        self.full_clean()
        # Update the crop season's current stage
        if self.crop_season.current_stage != self.stage:
            self.crop_season.current_stage = self.stage
            self.crop_season.save()
        super().save(*args, **kwargs)


class FieldUpdateAttachment(TimeStampedModel):
    """Attachments for field updates (photos of crops, issues, etc.)"""

    ATTACHMENT_TYPES = [
        ('crop_photo', 'Crop Photo'),
        ('issue_photo', 'Issue/Damage Photo'),
        ('measurement', 'Measurement Record'),
        ('weather_report', 'Weather Report'),
        ('pest_report', 'Pest/Disease Report'),
        ('other', 'Other'),
    ]

    field_update = models.ForeignKey('FieldUpdate', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='field_updates/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='Size in bytes')
    mime_type = models.CharField(max_length=100)
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='crop_photo')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Optional: Add location data for geotagged photos
    # location = gis_models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        db_table = 'field_update_attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field_update', 'attachment_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Update {self.field_update.id} - {self.filename}"

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name.split('/')[-1]
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class CropTypeAttachment(TimeStampedModel):
    """Attachments for crop types (reference images, growing guides, disease references, etc.)"""

    ATTACHMENT_TYPES = [
        ('reference_image', 'Reference Image'),
        ('growth_stage_guide', 'Growth Stage Guide'),
        ('disease_guide', 'Disease/Pest Guide'),
        ('variety_specs', 'Variety Specifications'),
        ('planting_guide', 'Planting Guide'),
        ('harvest_guide', 'Harvest Guide'),
        ('other', 'Other'),
    ]

    crop_type = models.ForeignKey('CropType', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='crop_types/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='Size in bytes')
    mime_type = models.CharField(max_length=100)
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='reference_image')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Optional: Link to specific growth stage
    growth_stage = models.CharField(
        max_length=50,
        choices=FieldUpdateStage.choices,
        blank=True,
        null=True,
        help_text="If this attachment relates to a specific growth stage"
    )

    class Meta:
        db_table = 'crop_type_attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['crop_type', 'attachment_type']),
            models.Index(fields=['growth_stage']),
        ]

    def __str__(self):
        return f"{self.crop_type.name} - {self.filename}"

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name.split('/')[-1]
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


