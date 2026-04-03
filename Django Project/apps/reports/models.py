import uuid
from django.db import models
from django.utils import timezone


ISSUE_CATEGORIES = [
    ('water', '💧 Water Leak'),
    ('electricity', '⚡ Electricity Fault'),
    ('roads', '🛣️ Road Damage'),
    ('waste', '🗑️ Waste Collection'),
    ('sewage', '🚿 Sewage'),
    ('lighting', '💡 Street Lighting'),
    ('other', '📋 Other'),
]

ISSUE_STATUS = [
    ('logged', 'Logged'),
    ('assigned', 'Assigned'),
    ('dispatched', 'Dispatched'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

CATEGORY_ICONS = {
    'water': '💧',
    'electricity': '⚡',
    'roads': '🛣️',
    'waste': '🗑️',
    'sewage': '🚿',
    'lighting': '💡',
    'other': '📋',
}


def generate_ref_id():
    """Generate a short human-readable reference ID."""
    uid = uuid.uuid4().hex[:8].upper()
    return f"CSR-{uid}"


class IssueReport(models.Model):
    ref_id = models.CharField(max_length=20, unique=True, default=generate_ref_id, editable=False)
    category = models.CharField(max_length=30, choices=ISSUE_CATEGORIES)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='issue_photos/', blank=True, null=True)

    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address_text = models.CharField(max_length=255, blank=True)
    ward = models.CharField(max_length=100, blank=True)

    # Reporter contact (optional, for notifications)
    reporter_phone = models.CharField(max_length=20, blank=True)
    reporter_name = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default='logged')
    whatsapp_sent = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    session_key = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue Report'
        verbose_name_plural = 'Issue Reports'

    def __str__(self):
        return f"{self.ref_id} — {self.get_category_display()} ({self.status})"

    @property
    def category_icon(self):
        return CATEGORY_ICONS.get(self.category, '📋')

    @property
    def category_label(self):
        return dict(ISSUE_CATEGORIES).get(self.category, self.category)

    @property
    def vote_count(self):
        return self.verifications.count()

    @property
    def days_open(self):
        delta = timezone.now() - self.created_at
        return delta.days

    @property
    def status_step(self):
        """Return numeric step (1-3) for progress indicator."""
        steps = {'logged': 1, 'assigned': 1, 'dispatched': 2, 'resolved': 3, 'closed': 3}
        return steps.get(self.status, 1)

    def get_status_display_label(self):
        return dict(ISSUE_STATUS).get(self.status, self.status)


class Verification(models.Model):
    """A 'I have this problem too' confirmation by another user."""
    issue = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='verifications')
    session_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('issue', 'session_key')
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for {self.issue.ref_id}"


class StatusLog(models.Model):
    """Track status changes over time."""
    issue = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, default='system')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.issue.ref_id}: {self.from_status} → {self.to_status}"
