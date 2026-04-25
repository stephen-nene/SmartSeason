# seasons/serializers.py
from rest_framework import serializers
from .models import CropSeason, FieldUpdate, CropType, FieldUpdateAttachment, CropTypeAttachment, FieldUpdateStage, SeasonStatus



class FieldUpdateAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldUpdateAttachment
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

class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropType
        fields = '__all__'

