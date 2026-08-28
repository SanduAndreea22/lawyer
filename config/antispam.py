"""Lightweight, dependency-free anti-spam helpers for public forms.

No API keys, no external service - a honeypot field plus a cache-based
per-IP rate limit. Good enough to stop basic bots hammering the contact
and booking forms; not a substitute for a real captcha or a rate-limiting
layer (nginx, Cloudflare, django-ratelimit) under real load. Note that the
default cache backend (LocMemCache) is per-process, so the rate limit is
per-worker in a multi-process deployment - still a meaningful throttle,
just not a hard global cap.
"""

from django import forms
from django.core.cache import cache

HONEYPOT_FIELD_NAME = "website"


class HoneypotMixin(forms.Form):
    """Adds an extra field real visitors never see or fill in.

    Rendered off-screen (not display:none - some bots skip fields hidden
    that way) via the `.hp-field` CSS class. A filled-in value means the
    submission is almost certainly automated; check `is_spam()` after the
    form validates and quietly drop it - don't tell the submitter why, or
    a bot operator adapts.
    """

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "hp-field",
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )

    def is_spam(self):
        return bool(self.cleaned_data.get(HONEYPOT_FIELD_NAME))


def is_rate_limited(request, key_prefix, limit=5, window_seconds=600):
    """True if this client IP has already hit `limit` submissions to
    `key_prefix` within `window_seconds`. Records this attempt either way."""
    ip = request.META.get("REMOTE_ADDR", "unknown")
    cache_key = f"ratelimit:{key_prefix}:{ip}"
    count = cache.get(cache_key, 0)
    if count >= limit:
        return True
    cache.set(cache_key, count + 1, window_seconds)
    return False
