from django.dispatch import receiver
from django.template.loader import render_to_string
from eventyay.control.signals import (
    event_dashboard_components,
    nav_event,
    nav_global,
)


@receiver(nav_global, dispatch_uid="socialmedia_nav")
def control_nav_socialmedia(sender, request=None, **kwargs):
    return []


@receiver(nav_event, dispatch_uid="socialmedia_nav_event")
def control_nav_event_socialmedia(sender, request=None, **kwargs):
    return []


@receiver(event_dashboard_components, dispatch_uid="socialmedia_dashboard_components")
def control_dashboard_socialmedia(sender, request=None, **kwargs):
    return render_to_string(
        "socialmedia/dashboard_component.html",
        {"request": request},
        request=request,
    )
