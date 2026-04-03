from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from apps.reports.models import IssueReport, Verification, StatusLog
from .serializers import IssueReportSerializer, IssueReportGeoSerializer


class IssueReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for issue reports.
    GET  /api/issues/          — list all issues (GeoJSON)
    POST /api/issues/          — create new issue
    GET  /api/issues/<id>/     — retrieve single issue
    POST /api/issues/<id>/verify/  — verify / confirm an issue
    GET  /api/issues/<id>/status/  — get status log
    """
    queryset = IssueReport.objects.annotate(
        vote_count=Count('verifications')
    ).order_by('-created_at')
    serializer_class = IssueReportSerializer

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('format') == 'geojson':
            return IssueReportGeoSerializer
        return IssueReportSerializer

    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """POST /api/issues/<id>/verify/ — add a '+1 Issue' confirmation."""
        issue = self.get_object()
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        verification, created = Verification.objects.get_or_create(
            issue=issue,
            session_key=session_key,
        )
        if not created:
            # Allow toggle: remove if already verified
            verification.delete()
            return Response({
                'status': 'removed',
                'vote_count': issue.verifications.count(),
            })

        return Response({
            'status': 'confirmed',
            'vote_count': issue.verifications.count(),
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='status')
    def status_log(self, request, pk=None):
        """GET /api/issues/<id>/status/ — return status history."""
        issue = self.get_object()
        logs = issue.status_logs.all().values(
            'from_status', 'to_status', 'note', 'created_at', 'created_by'
        )
        return Response({
            'ref_id': issue.ref_id,
            'current_status': issue.status,
            'status_step': issue.status_step,
            'history': list(logs),
        })

    def list(self, request, *args, **kwargs):
        """Return GeoJSON FeatureCollection for Leaflet maps."""
        qs = self.get_queryset()

        # Optional filters
        cat = request.query_params.get('category')
        if cat:
            qs = qs.filter(category=cat)
        stat = request.query_params.get('status')
        if stat:
            qs = qs.filter(status=stat)

        # GeoJSON response
        features = []
        for issue in qs.filter(latitude__isnull=False, longitude__isnull=False):
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(issue.longitude), float(issue.latitude)],
                },
                'properties': {
                    'id': issue.pk,
                    'ref_id': issue.ref_id,
                    'category': issue.category,
                    'category_label': issue.category_label,
                    'icon': issue.category_icon,
                    'description': issue.description[:100] if issue.description else '',
                    'vote_count': issue.vote_count,
                    'days_open': issue.days_open,
                    'status': issue.status,
                    'address_text': issue.address_text,
                },
            })

        return Response({
            'type': 'FeatureCollection',
            'features': features,
        })
