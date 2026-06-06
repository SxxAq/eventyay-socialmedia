from django.urls import path

from eventyay.common.urls import OrganizerSlugConverter  # noqa: F401
from . import views

app_name = "socialmedia"

urlpatterns = [
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/",
        views.index,
        name="index",
    ),
    path(
        "control/socialmedia/",
        views.global_index,
        name="global_index",
    ),
]
