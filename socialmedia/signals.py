from django.dispatch import receiver
from eventyay.control.signals import nav_event, nav_global


@receiver(nav_global, dispatch_uid="socialmedia_nav")
def control_nav_socialmedia(sender, request=None, **kwargs):
    return []


@receiver(nav_event, dispatch_uid="socialmedia_nav_event")
def control_nav_event_socialmedia(sender, request=None, **kwargs):
    return []
