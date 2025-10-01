# clinic/templatetags/custom_filters.py
import os
from django import template

register = template.Library()

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
