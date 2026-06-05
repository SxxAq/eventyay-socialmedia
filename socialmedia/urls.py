from django.urls import path

from eventyay.common.urls import OrganizerSlugConverter  # noqa: F401
from . import views

app_name = "socialmedia"

urlpatterns = [
    path(
        "social/event/<orgslug:organizer>/<slug:event>/",
        views.index,
        name="index",
    ),
    path(
        "social/",
        views.global_index,
        name="global_index",
    ),
]


