from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.http import JsonResponse
from .models import IssueReport, StatusLog, ISSUE_CATEGORIES, CATEGORY_ICONS
from .forms import LocationForm, ReportSubmitForm


class HomeView(TemplateView):
    """Screen 1 — Home / Landing."""
    template_name = 'report/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = ISSUE_CATEGORIES
        ctx['category_icons'] = CATEGORY_ICONS
        ctx['recent_count'] = IssueReport.objects.filter(status__in=['logged', 'dispatched']).count()
        return ctx


class LocationView(View):
    """Screen 2 — Location picker (GPS + text fallback)."""
    template_name = 'report/location.html'

    def get(self, request):
        form = LocationForm()
        category = request.GET.get('category', '')
        return render(request, self.template_name, {
            'form': form,
            'category': category,
            'category_icons': CATEGORY_ICONS,
        })

    def post(self, request):
        form = LocationForm(request.POST)
        if form.is_valid():
            # Store location in session
            request.session['report_latitude'] = form.cleaned_data.get('latitude', '')
            request.session['report_longitude'] = form.cleaned_data.get('longitude', '')
            request.session['report_address'] = form.cleaned_data.get('address_text', '')
            request.session['report_category'] = request.POST.get('category', '')
            return redirect('report:submit')
        return render(request, self.template_name, {'form': form, 'category_icons': CATEGORY_ICONS})


class ReportSubmitView(View):
    """Screen 3 — Report form with description, photo, voice."""
    template_name = 'report/submit.html'

    def get(self, request):
        form = ReportSubmitForm(initial={
            'category': request.session.get('report_category', ''),
        })
        return render(request, self.template_name, {
            'form': form,
            'category': request.session.get('report_category', ''),
            'address': request.session.get('report_address', ''),
            'categories': ISSUE_CATEGORIES,
            'category_icons': CATEGORY_ICONS,
        })

    def post(self, request):
        form = ReportSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.latitude = request.session.get('report_latitude') or None
            report.longitude = request.session.get('report_longitude') or None
            report.address_text = request.session.get('report_address', '')
            report.session_key = request.session.session_key or ''
            report.save()

            # Log initial status
            StatusLog.objects.create(
                issue=report,
                from_status='',
                to_status='logged',
                created_by='user',
                note='Issue reported by community member.',
            )

            # Clear session data
            for key in ['report_latitude', 'report_longitude', 'report_address', 'report_category']:
                request.session.pop(key, None)

            return redirect('report:done', ref_id=report.ref_id)

        return render(request, self.template_name, {
            'form': form,
            'categories': ISSUE_CATEGORIES,
            'category_icons': CATEGORY_ICONS,
            'address': request.session.get('report_address', ''),
        })


class ReportDoneView(TemplateView):
    """Screen 4 — Confirmation / Success screen."""
    template_name = 'report/done.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        report = get_object_or_404(IssueReport, ref_id=kwargs['ref_id'])
        ctx['report'] = report
        ctx['whatsapp_sent'] = report.whatsapp_sent
        return ctx


class IssueMapView(TemplateView):
    """Screen 5 — Community issue map."""
    template_name = 'map/issue_map.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        issues = IssueReport.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            status__in=['logged', 'assigned', 'dispatched'],
        ).select_related()
        ctx['issues'] = issues
        ctx['issues_geojson'] = self._build_geojson(issues)
        ctx['featured_issues'] = IssueReport.objects.all()[:5]
        return ctx

    def _build_geojson(self, issues):
        import json
        features = []
        for issue in issues:
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
                    'icon': issue.category_icon,
                    'label': issue.category_label,
                    'vote_count': issue.vote_count,
                    'days_open': issue.days_open,
                    'status': issue.status,
                },
            })
        return json.dumps({'type': 'FeatureCollection', 'features': features})
