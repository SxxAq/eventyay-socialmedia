from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from eventyay.base.models import Event
from eventyay.eventyay_common.navigation import get_event_navigation


@login_required
def index(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)

    # Permission check
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()

    # Check if plugin is enabled
    if "socialmedia" not in event_obj.plugin_list:
        raise Http404("Social Media plugin is not enabled for this event.")

    # Populate navigation items for the sidebar
    request.event = event_obj
    request.organizer = event_obj.organizer
    nav_items = get_event_navigation(request, event_obj)

    return render(
        request,
        "socialmedia/index.html",
        {
            "event": event_obj,
            "nav_items": nav_items,
        },
    )
