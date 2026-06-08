from datetime import timedelta
import pytest
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils.timezone import now
from django_scopes import scope

from eventyay.base.models import Event, Organizer, Team, User
from socialmedia.models import SocialMediaAccount, SocialPost


@pytest.fixture(autouse=True)
def override_site_url(settings):
    settings.SITE_URL = "https://testserver"



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
        plugins="socialmedia",
    )


@pytest.fixture
def user():
    return User.objects.create_user(email="testuser@test.com", password="password")


@pytest.mark.django_db
def test_global_index_logged_out(client):
    url = reverse("plugins:socialmedia:global_index")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_global_index_logged_in(client, user, organizer, event):
    # Enable the plugin on the event
    event.plugins = "socialmedia"
    event.save()

    # User with permission
    team = Team.objects.create(
        organizer=organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)

    client.force_login(user)
    url = reverse("plugins:socialmedia:global_index")
    response = client.get(url)
    assert response.status_code == 200
    assert event in [item["event"] for item in response.context["events_data"]]


@pytest.mark.django_db
def test_global_index_logged_in_no_plugin(client, user, organizer, event):
    # Disable the plugin
    event.plugins = ""
    event.save()

    team = Team.objects.create(
        organizer=organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)

    client.force_login(user)
    url = reverse("plugins:socialmedia:global_index")
    response = client.get(url)
    assert response.status_code == 200
    assert event not in [item["event"] for item in response.context["events_data"]]


@pytest.mark.django_db
def test_event_index_logged_out(client, event):
    url = reverse(
        "plugins:socialmedia:index",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_event_index_no_permission(client, user, event):
    # User is logged in but has no team membership/permission
    client.force_login(user)
    url = reverse(
        "plugins:socialmedia:index",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_event_index_plugin_disabled(client, user, event):
    # User has permission, but plugin is disabled
    event.plugins = ""
    event.save()

    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)

    client.force_login(user)
    url = reverse(
        "plugins:socialmedia:index",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_event_index_success(client, user, event):
    # User has permission and plugin is enabled
    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)

    # Let's create some database records to check statistics logic
    with scope(event=event):
        account1 = SocialMediaAccount.objects.create(
            event=event,
            provider="mastodon",
            account_name="test_mastodon",
            credentials="{}",
            is_active=True,
        )
        account2 = SocialMediaAccount.objects.create(
            event=event,
            provider="twitter",
            account_name="test_twitter_inactive",
            credentials="{}",
            is_active=False,
        )

        # Draft
        SocialPost.objects.create(
            event=event,
            account=account1,
            text="Draft post",
            status="draft",
        )
        # Scheduled
        SocialPost.objects.create(
            event=event,
            account=account1,
            text="Scheduled post",
            status="scheduled",
        )
        # Published
        SocialPost.objects.create(
            event=event,
            account=account1,
            text="Published post",
            status="published",
        )
        # Failed
        SocialPost.objects.create(
            event=event,
            account=account1,
            text="Failed post",
            status="failed",
        )

    client.force_login(user)
    url = reverse(
        "plugins:socialmedia:index",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.get(url)
    assert response.status_code == 200

    # Assert stats
    assert response.context["draft_count"] == 1
    assert response.context["scheduled_count"] == 1
    assert response.context["published_count"] == 1
    assert response.context["failed_count"] == 1

    # Assert accounts (now it returns all connected accounts)
    assert account1 in response.context["accounts"]
    assert account2 in response.context["accounts"]


@pytest.mark.django_db
def test_export_posts_csv(client, user, event):
    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)
    client.force_login(user)

    url = reverse(
        "plugins:socialmedia:export_posts_csv",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert f"social_posts_{event.slug}.csv" in response["Content-Disposition"]


@pytest.mark.django_db
def test_account_create_delete(client, user, event):
    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)
    client.force_login(user)

    # Create account
    create_url = reverse(
        "plugins:socialmedia:account_create",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.post(
        create_url, {"provider": "twitter", "account_name": "new_handle"}
    )
    assert response.status_code == 302

    with scope(event=event):
        account = SocialMediaAccount.objects.get(
            provider="twitter", account_name="new_handle"
        )
        assert account.is_active

    # Delete account
    delete_url = reverse(
        "plugins:socialmedia:account_delete",
        kwargs={
            "organizer": event.organizer.slug,
            "event": event.slug,
            "pk": account.pk,
        },
    )
    response = client.post(delete_url)
    assert response.status_code == 302
    with scope(event=event):
        assert not SocialMediaAccount.objects.filter(pk=account.pk).exists()


@pytest.mark.django_db
def test_template_create_delete(client, user, event):
    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)
    client.force_login(user)

    create_url = reverse(
        "plugins:socialmedia:template_create",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.post(
        create_url, {"name": "Test Template", "template_text": "Text {event_name}"}
    )
    assert response.status_code == 302

    with scope(event=event):
        template = PostTemplate.objects.get(name="Test Template")
        assert template.template_text == "Text {event_name}"

    delete_url = reverse(
        "plugins:socialmedia:template_delete",
        kwargs={
            "organizer": event.organizer.slug,
            "event": event.slug,
            "pk": template.pk,
        },
    )
    response = client.post(delete_url)
    assert response.status_code == 302
    with scope(event=event):
        assert not PostTemplate.objects.filter(pk=template.pk).exists()


@pytest.mark.django_db
def test_rule_create_delete(client, user, event):
    team = Team.objects.create(
        organizer=event.organizer,
        all_events=True,
        can_change_event_settings=True,
    )
    team.members.add(user)
    client.force_login(user)

    with scope(event=event):
        template = PostTemplate.objects.create(
            event=event,
            name="Announcement",
            template_text="Welcome to {event_name}!",
        )

    create_url = reverse(
        "plugins:socialmedia:rule_create",
        kwargs={"organizer": event.organizer.slug, "event": event.slug},
    )
    response = client.post(
        create_url,
        {
            "template": template.pk,
            "trigger_type": "before_event",
            "offset_minutes": "1440",
        },
    )
    assert response.status_code == 302

    with scope(event=event):
        rule = ScheduleRule.objects.get(
            template=template, trigger_type="before_event"
        )
        assert rule.offset_minutes == 1440

    delete_url = reverse(
        "plugins:socialmedia:rule_delete",
        kwargs={
            "organizer": event.organizer.slug,
            "event": event.slug,
            "pk": rule.pk,
        },
    )
    response = client.post(delete_url)
    assert response.status_code == 302
    with scope(event=event):
        assert not ScheduleRule.objects.filter(pk=rule.pk).exists()

