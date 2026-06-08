from django.db import models
from django.utils.translation import gettext_lazy as _
from django_scopes import ScopedManager
from eventyay.base.models import Event


class SocialMediaAccount(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="social_accounts"
    )
    provider = models.CharField(max_length=50)
    account_name = models.CharField(max_length=255)
    credentials = models.TextField()  # store encrypted JSON
    is_active = models.BooleanField(default=True)

    objects = ScopedManager(organizer="event__organizer", event="event")

    class Meta:
        unique_together = ("event", "provider", "account_name")
        verbose_name = _("Social Media Account")
        verbose_name_plural = _("Social Media Accounts")

    def __str__(self):
        return f"{self.provider} / {self.account_name} ({self.event.slug})"


class SocialPost(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("scheduled", "Scheduled"),
        ("publishing", "Publishing"),
        ("published", "Published"),
        ("failed", "Failed"),
    ]
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="social_posts"
    )
    account = models.ForeignKey(
        SocialMediaAccount, on_delete=models.PROTECT, related_name="posts"
    )
    text = models.TextField()
    media = models.FileField(upload_to="socialmedia/posts/", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True
    )
    scheduled_time = models.DateTimeField(null=True, blank=True, db_index=True)
    published_time = models.DateTimeField(null=True, blank=True)
    external_post_id = models.CharField(max_length=255, null=True, blank=True)
    talk_slot = models.ForeignKey(
        "base.TalkSlot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="social_posts",
    )

    objects = ScopedManager(organizer="event__organizer", event="event")

    class Meta:
        verbose_name = _("Social Post")
        verbose_name_plural = _("Social Posts")
        ordering = ("-scheduled_time",)

    def __str__(self):
        return (
            f"{self.event.slug} | {self.get_status_display()} | {self.scheduled_time}"
        )


class PostTemplate(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="social_templates"
    )
    name = models.CharField(max_length=255)
    template_text = models.TextField()
    is_active = models.BooleanField(default=True)

    objects = ScopedManager(organizer="event__organizer", event="event")

    class Meta:
        verbose_name = _("Post Template")
        verbose_name_plural = _("Post Templates")
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.event.slug})"


class ScheduleRule(models.Model):
    TRIGGER_CHOICES = [
        ("before_event", _("Before Event Starts")),
        ("after_event", _("After Event Ends")),
        ("before_session", _("Before Session Starts")),
        ("after_session", _("After Session Ends")),
    ]
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="social_schedule_rules"
    )
    template = models.ForeignKey(
        PostTemplate,
        on_delete=models.CASCADE,
        related_name="schedule_rules",
    )
    trigger_type = models.CharField(
        max_length=30, choices=TRIGGER_CHOICES, verbose_name=_("Trigger Type")
    )
    offset_minutes = models.IntegerField(verbose_name=_("Offset (in minutes)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    objects = ScopedManager(organizer="event__organizer", event="event")

    class Meta:
        verbose_name = _("Schedule Rule")
        verbose_name_plural = _("Schedule Rules")
        ordering = ("offset_minutes",)

    def __str__(self):
        return f"Rule {self.pk or 'new'} ({self.offset_minutes}m)"


class SocialPostAuditLog(models.Model):
    post = models.ForeignKey(
        SocialPost, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(max_length=100)
    from_status = models.CharField(max_length=50, null=True, blank=True)
    to_status = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(
        "base.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="social_post_audits",
    )
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ScopedManager(organizer="post__event__organizer", event="post__event")

    class Meta:
        verbose_name = _("Social Post Audit Log")
        verbose_name_plural = _("Social Post Audit Logs")
        ordering = ("-timestamp",)

    def __str__(self):
        return f"Audit {self.pk or 'new'} - Post {self.post_id}: {self.action} at {self.timestamp}"
