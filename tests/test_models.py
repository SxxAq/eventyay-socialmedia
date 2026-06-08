from datetime import timedelta
from django.db.utils import IntegrityError
from django.utils.timezone import now
import pytest
from django_scopes import scope

from eventyay.base.models import Event, Organizer
from socialmedia.models import (
    SocialMediaAccount,
    SocialPost,
    PostTemplate,
    ScheduleRule,
    SocialPostAuditLog,
)


@pytest.fixture
def organizer(db):
    return Organizer.objects.create(name="Test Org", slug="test-org")


@pytest.fixture
def event(organizer):
    return Event.objects.create(
        name="Test Event",
        slug="test-event",
        organizer=organizer,
        date_from=now(),
        date_to=now() + timedelta(days=1),
    )


@pytest.fixture
def event2(organizer):
    return Event.objects.create(
        name="Test Event 2",
        slug="test-event-2",
        organizer=organizer,
        date_from=now(),
        date_to=now() + timedelta(days=1),
    )


@pytest.mark.django_db
def test_social_media_account_creation(event):
    with scope(event=event):
        account = SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_account",
            credentials='{"token": "xyz"}',
        )
        assert account.provider == "mastodon"
        assert account.account_name == "test_account"
        assert str(account) == "mastodon / test_account (test-event)"


@pytest.mark.django_db
def test_social_media_account_uniqueness(event):
    with scope(event=event):
        SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_account",
            credentials='{"token": "xyz"}',
        )
        with pytest.raises(IntegrityError):
            SocialMediaAccount.objects.create(
                event=event,
                provider="mastodon",
                account_name="test_account",
                credentials='{"token": "abc"}',
            )


@pytest.mark.django_db
def test_social_post_creation(event):
    with scope(event=event):
        account = SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_account",
            credentials='{"token": "xyz"}',
        )
        post = SocialPost.objects.create(
            event=event,
            account=account,
            text="Hello World!",
            status="draft",
        )
        assert post.text == "Hello World!"
        assert post.status == "draft"
        assert str(post).startswith("test-event | Draft | None")


@pytest.mark.django_db
def test_post_template_creation(event):
    with scope(event=event):
        template = PostTemplate.objects.create(
            event=event,
            name="Announcement",
            template_text="Welcome to {event_name}!",
        )
        assert template.name == "Announcement"
        assert str(template) == "Announcement (test-event)"


@pytest.mark.django_db
def test_schedule_rule_creation(event):
    with scope(event=event):
        template = PostTemplate.objects.create(
            event=event,
            name="Announcement",
            template_text="Welcome to {event_name}!",
        )
        rule = ScheduleRule.objects.create(
            event=event,
            template=template,
            trigger_type="before_event",
            offset_minutes=1440,
        )
        assert rule.offset_minutes == 1440
        assert str(rule) == f"Rule {rule.pk} (1440m)"


@pytest.mark.django_db
def test_social_post_audit_log_creation(event):
    with scope(event=event):
        account = SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_account",
            credentials='{"token": "xyz"}',
        )
        post = SocialPost.objects.create(
            event=event,
            account=account,
            text="Hello World!",
            status="draft",
        )
        log = SocialPostAuditLog.objects.create(
            post=post,
            action="status_change",
            from_status="draft",
            to_status="submitted",
        )
        assert log.action == "status_change"
        assert log.from_status == "draft"
        assert log.to_status == "submitted"
        assert str(log).startswith("Audit")


@pytest.mark.django_db
def test_cross_event_query_blocking(event, event2):
    with scope(event=event):
        SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_account",
            credentials='{"token": "xyz"}',
        )

    with scope(event=event2):
        assert SocialMediaAccount.objects.count() == 0
