from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from eventyay.control.signals import nav_event, nav_global


@receiver(nav_global, dispatch_uid="socialmedia_nav")
def control_nav_socialmedia(sender, request=None, **kwargs):
    if not request or not request.user.is_authenticated:
        return []
    url = resolve(request.path_info)
    return [
        {
            "label": _("Social Media"),
            "url": reverse("plugins:socialmedia:global_index"),
            "icon": "share-square-o",
            "active": (
                url.namespace == "plugins:socialmedia"
                and url.url_name == "global_index"
            ),
        }
    ]


@receiver(nav_event, dispatch_uid="socialmedia_nav_event")
def control_nav_event_socialmedia(sender, request=None, **kwargs):
    if not request or not request.user.is_authenticated:
        return []
    url = resolve(request.path_info)
    return [
        {
            "label": _("Social Media"),
            "url": reverse(
                "plugins:socialmedia:index",
                kwargs={
                    "organizer": sender.organizer.slug,
                    "event": sender.slug,
                },
            ),
            "icon": "share-square-o",
            "active": (
                url.namespace == "plugins:socialmedia" and url.url_name == "index"
            ),
        }
    ]
