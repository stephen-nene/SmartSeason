from django.db import models

from django.core.exceptions import ValidationError

# Create your models here.



class FieldUpdateStage(models.TextChoices):
    PLANTED = "planted"
    GROWING = "growing"
    READY = "ready"
    HARVESTED = "harvested"

    PLANTING = "planting"
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"

    FLOWERING = "flowering"
    FRUITING = "fruiting"
    HARVEST = "harvest"
    DORMANT = "dormant"


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
    field  = models.ForeignKey('profiles.Field', on_delete=models.CASCADE)
    crop_type = models.ForeignKey(CropType, on_delete=models.CASCADE)
    # crop_type = models.CharField(max_length=50)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    actual_harvest_date = models.DateField(blank=True, null=True)
    current_stage = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, choices=SeasonStatus.choices, default=SeasonStatus.ACTIVE)
    created_by = models.ForeignKey('profiles.User', on_delete=models.CASCADE)


    def calculate_status(self):
        """Calculate season status based on planting date, expected harvest, and updates"""
        from datetime import date, timedelta
        from django.utils import timezone

        today = timezone.now().date()

        if self.actual_harvest_date:
            return SeasonStatus.COMPLETED

        if self.current_stage == FieldUpdateStage.HARVESTED:
            return SeasonStatus.COMPLETED

        # Calculate days since planting
        days_since_planting = (today - self.planting_date).days

        # Check if past expected harvest date
        if today > self.expected_harvest_date:
            return SeasonStatus.AT_RISK

        # Check for delayed growth (no updates in last 7 days)
        last_update = self.fieldupdate_set.order_by('-created_at').first()
        if last_update and (today - last_update.created_at.date()).days > 7:
            if self.current_stage not in [FieldUpdateStage.READY, FieldUpdateStage.HARVESTED]:
                return SeasonStatus.AT_RISK

        # Check for growth stage delays
        expected_stages = {
            FieldUpdateStage.PLANTED: 0,
            FieldUpdateStage.GROWING: 14,
            FieldUpdateStage.READY: 45,
        }

        if self.current_stage in expected_stages:
            expected_days = expected_stages[self.current_stage]
            if days_since_planting > expected_days + 14:  # 2 weeks buffer
                return SeasonStatus.AT_RISK

        return SeasonStatus.ACTIVE

    def save(self, *args, **kwargs):
        # Update status automatically
        if not self.actual_harvest_date:
            self.status = self.calculate_status()
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
                fields= ["field", "status"],
                condition=models.Q(status="active"),
                name="one_active_season_per_field"
            )
        ]

class FieldAssignment(models.Model):
    # crop_season = models.ForeignKey(CropSeason, on_delete=models.CASCADE)
    # This allows an agent handles ALL seasons self.field
    field = models.ForeignKey('profiles.Field', on_delete=models.CASCADE)
    agent = models.ForeignKey('profiles.User', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('profiles.User', on_delete=models.CASCADE)

    def __str__(self):
        # return f"{self.user.username} - {self.crop_season_id.field.name}"
        return f"{self.agent.username} -  {self.field.name}"

    class Meta:
        # pass
        unique_together = ('field', 'agent')
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["user"],
        #         condition=models.Q(crop_season__status="active"),
        #         name="one_active_season_per_agent"
        #     )
        # ]

class FieldUpdate(TimeStampedModel):
    crop_season = models.ForeignKey(CropSeason, on_delete=models.CASCADE)
    agent = models.ForeignKey('profiles.User', on_delete=models.CASCADE)
    stage = models.CharField(max_length=50, choices=FieldUpdateStage.choices, null=False, blank=False)
    notes = models.TextField()
    health_status = models.CharField(max_length=50)

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

