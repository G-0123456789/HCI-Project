from rest_framework import serializers
from apps.reports.models import IssueReport, Verification, StatusLog


class StatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusLog
        fields = ['from_status', 'to_status', 'note', 'created_at', 'created_by']


class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['id', 'created_at']


class IssueReportSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()
    days_open = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    category_icon = serializers.SerializerMethodField()
    status_step = serializers.SerializerMethodField()
    status_logs = StatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = IssueReport
        fields = [
            'id', 'ref_id', 'category', 'category_label', 'category_icon',
            'description', 'photo', 'latitude', 'longitude', 'address_text',
            'ward', 'reporter_name', 'reporter_phone', 'status', 'status_step',
            'whatsapp_sent', 'created_at', 'updated_at',
            'vote_count', 'days_open', 'status_logs',
        ]
        read_only_fields = ['ref_id', 'created_at', 'updated_at', 'whatsapp_sent']

    def get_vote_count(self, obj):
        return obj.verifications.count()

    def get_days_open(self, obj):
        return obj.days_open

    def get_category_label(self, obj):
        return obj.category_label

    def get_category_icon(self, obj):
        return obj.category_icon

    def get_status_step(self, obj):
        return obj.status_step


class IssueReportGeoSerializer(IssueReportSerializer):
    """GeoJSON-compatible serializer."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    float(instance.longitude) if instance.longitude else None,
                    float(instance.latitude) if instance.latitude else None,
                ],
            },
            'properties': data,
        }
