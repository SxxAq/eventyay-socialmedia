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
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/export/",
        views.export_posts_csv,
        name="export_posts_csv",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/accounts/create/",
        views.account_create,
        name="account_create",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/accounts/<int:pk>/delete/",
        views.account_delete,
        name="account_delete",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/templates/create/",
        views.template_create,
        name="template_create",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/templates/<int:pk>/delete/",
        views.template_delete,
        name="template_delete",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/rules/create/",
        views.rule_create,
        name="rule_create",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/rules/<int:pk>/delete/",
        views.rule_delete,
        name="rule_delete",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/posts/create/",
        views.post_create,
        name="post_create",
    ),
    path(
        "control/event/<orgslug:organizer>/<slug:event>/socialmedia/posts/<int:pk>/delete/",
        views.post_delete,
        name="post_delete",
    ),
]
