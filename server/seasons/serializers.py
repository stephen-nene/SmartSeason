# seasons/serializers.py
from rest_framework import serializers
from .models import CropSeason, FieldUpdate, CropType, FieldUpdateAttachment, CropTypeAttachment, FieldUpdateStage, SeasonStatus



class FieldUpdateAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldUpdateAttachment
        fields = '__all__'
        
class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropType
        fields = '__all__'


class FieldUpdateSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.username', read_only=True)

    class Meta:
        model = FieldUpdate
        fields = ['id', 'stage', 'notes', 'created_at', 'agent_name']
        read_only_fields = ['agent', 'created_at']

class CropSeasonSerializer(serializers.ModelSerializer):
    updates = FieldUpdateSerializer(many=True, read_only=True)
    computed_status = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    days_since_planting = serializers.ReadOnlyField()

    class Meta:
        model = CropSeason
        fields = '__all__'
        read_only_fields = ['status', 'current_stage', 'created_at', 'updated_at']


class CropSeasonDetailSerializer(serializers.ModelSerializer):
    """Detailed season info used in field detail view"""
    crop_type = CropTypeSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_stage_display = serializers.CharField(source='get_current_stage_display', read_only=True)
    days_since_planting = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    days_until_harvest = serializers.SerializerMethodField()
    recent_updates = serializers.SerializerMethodField()

    class Meta:
        model = CropSeason
        fields = [
            'id', 'name', 'crop_type', 'planting_date',
            'expected_harvest_date', 'actual_harvest_date',
            'status', 'status_display', 'current_stage',
            'current_stage_display', 'active', 'days_since_planting',
            'progress_percentage', 'days_until_harvest',
            'created_by', 'created_by_name', 'recent_updates',
            'created_at', 'updated_at'
        ]

    def get_days_until_harvest(self, obj):
        """Calculate days remaining until expected harvest"""
        from django.utils import timezone
        if obj.actual_harvest_date:
            return 0
        remaining = (obj.expected_harvest_date - timezone.now().date()).days
        return max(0, remaining)

    def get_recent_updates(self, obj):
        """Get last 5 updates for this season"""
        recent = obj.fieldupdate_set.order_by('-created_at')[:5]
        return FieldUpdateSerializer(recent, many=True).data


