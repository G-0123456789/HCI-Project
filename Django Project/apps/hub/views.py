from django.shortcuts import render
from django.views.generic import ListView
from apps.reports.models import IssueReport
from django.db.models import Count


class CommunityHubView(ListView):
    """Screen 6 — Community Hub with prioritised issues."""
    template_name = 'hub/community.html'
    context_object_name = 'issues'

    def get_queryset(self):
        return (
            IssueReport.objects
            .annotate(vote_count=Count('verifications'))
            .order_by('-vote_count', '-created_at')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_issues'] = self.get_queryset().filter(
            status__in=['logged', 'assigned', 'dispatched']
        )
        ctx['resolved_issues'] = self.get_queryset().filter(
            status__in=['resolved', 'closed']
        )
        return ctx
