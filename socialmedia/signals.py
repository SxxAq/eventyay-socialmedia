from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from eventyay.control.signals import nav_global


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
            ),
        }
    ]
