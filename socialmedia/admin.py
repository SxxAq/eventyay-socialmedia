from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    SocialMediaAccount,
    SocialPost,
    PostTemplate,
    ScheduleRule,
    SocialPostAuditLog,
)


@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ("account_name", "provider", "event", "is_active")
    list_filter = ("provider", "is_active", "event")
    search_fields = ("account_name", "event__name", "event__slug")
    fieldsets = (
        (None, {"fields": ("event", "provider", "account_name", "is_active")}),
        (
            _("Credentials & Details"),
            {
                "fields": ("credentials",),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "account",
        "status",
        "scheduled_time",
        "published_time",
    )
    list_filter = ("status", "account__provider", "event")
    search_fields = ("text", "event__name", "event__slug", "account__account_name")
    fieldsets = (
        (None, {"fields": ("event", "account", "text", "media", "status")}),
        (
            _("Scheduling & Publication"),
            {
                "fields": (
                    "scheduled_time",
                    "published_time",
                    "external_post_id",
                    "talk_slot",
                )
            },
        ),
    )


@admin.register(PostTemplate)
class PostTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "is_active")
    list_filter = ("is_active", "event")
    search_fields = ("name", "template_text", "event__name")


@admin.register(ScheduleRule)
class ScheduleRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "template",
        "trigger_type",
        "offset_minutes",
        "is_active",
    )
    list_filter = ("trigger_type", "is_active", "event")
    search_fields = ("template__name", "event__name", "event__slug")


@admin.register(SocialPostAuditLog)
class SocialPostAuditLogAdmin(admin.ModelAdmin):
    list_display = ("post", "action", "from_status", "to_status", "user", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("post__text", "user__email", "user__username")
    readonly_fields = (
        "post",
        "action",
        "from_status",
        "to_status",
        "user",
        "details",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
