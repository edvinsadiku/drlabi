"""Server-side access policy for clinic-wide reports."""
from datetime import date, timedelta

from django.core.exceptions import PermissionDenied
from django.utils import timezone


def report_day(request):
    """Resolve a local calendar day; staff may request only today or yesterday."""
    today = timezone.localdate()
    try:
        day = date.fromisoformat(request.GET.get("day") or today.isoformat())
    except (TypeError, ValueError):
        raise PermissionDenied("Data e raportit nuk është e vlefshme.")
    if not request.user.is_superuser:
        mode = (request.GET.get("mode") or "day").lower()
        if mode != "day" or day not in {today, today - timedelta(days=1)}:
            raise PermissionDenied("Mund të shihni vetëm raportin e sotëm ose të djeshëm.")
    return day


def require_full_reports(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Ky raport është i disponueshëm vetëm për superadminin.")


def day_navigation():
    today = timezone.localdate()
    return {"today": today, "yesterday": today - timedelta(days=1)}
