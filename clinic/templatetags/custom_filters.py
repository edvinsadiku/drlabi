# clinic/templatetags/custom_filters.py
import os
import hashlib
from functools import lru_cache
from pathlib import Path
from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@lru_cache(maxsize=128)
def _asset_digest(path, modified_ns, size):
    # The stat values invalidate the cached digest whenever a source asset changes.
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


@register.simple_tag
def versioned_static(name):
    """Give changed assets a new URL so an old browser cache cannot mix releases."""
    url = static(name)
    path = finders.find(name)
    if not path:
        return url
    info = os.stat(path)
    version = _asset_digest(path, info.st_mtime_ns, info.st_size)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={version}"

@register.filter
def basename(value):
    """Kthen vetëm emrin e file nga path"""
    if not value:
        return ""
    return os.path.basename(str(value))

@register.filter
def extension(value):
    """Kthen extension e file-it (p.sh. PDF, DOCX, JPG)"""
    if not value:
        return ""
    name = os.path.basename(str(value))
    ext = os.path.splitext(name)[1].replace(".", "").upper()
    return ext or "FILE"
