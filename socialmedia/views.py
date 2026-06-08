import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_scopes import scope

from eventyay.base.models import Event
from socialmedia.models import (
    PostTemplate,
    ScheduleRule,
    SocialMediaAccount,
    SocialPost,
)


@login_required
def global_index(request):
    # Fetch all events where the user has settings permission
    user_events = request.user.get_events_with_permission(
        "can_change_event_settings", request=request
    )

    # Filter events where the socialmedia plugin is enabled
    events = [e for e in user_events if "socialmedia" in e.plugin_list]

    events_data = []
    for event_obj in events:
        with scope(event=event_obj):
            draft_count = SocialPost.objects.filter(
                event=event_obj, status__in=["draft", "submitted", "approved"]
            ).count()
            scheduled_count = SocialPost.objects.filter(
                event=event_obj, status__in=["scheduled", "publishing"]
            ).count()
            published_count = SocialPost.objects.filter(
                event=event_obj, status="published"
            ).count()
            failed_count = SocialPost.objects.filter(
                event=event_obj, status="failed"
            ).count()
            events_data.append({
                "event": event_obj,
                "drafts": draft_count,
                "scheduled": scheduled_count,
                "published": published_count,
                "failed": failed_count,
            })

    return render(
        request,
        "socialmedia/global_index.html",
        {"events_data": events_data},
    )


@login_required
def index(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)

    # Permission check
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()

    # Check if plugin is enabled
    if "socialmedia" not in event_obj.plugin_list:
        raise Http404("Social Media plugin is not enabled for this event.")

    # Fetch stats and accounts within the scope of the event
    with scope(event=event_obj):
        draft_count = SocialPost.objects.filter(
            event=event_obj, status__in=["draft", "submitted", "approved"]
        ).count()
        scheduled_count = SocialPost.objects.filter(
            event=event_obj, status__in=["scheduled", "publishing"]
        ).count()
        published_count = SocialPost.objects.filter(
            event=event_obj, status="published"
        ).count()
        failed_count = SocialPost.objects.filter(
            event=event_obj, status="failed"
        ).count()

        accounts = SocialMediaAccount.objects.filter(event=event_obj)
        templates = PostTemplate.objects.filter(event=event_obj)
        rules = ScheduleRule.objects.filter(event=event_obj)
        posts = SocialPost.objects.filter(event=event_obj)

    context = {
        "event": event_obj,
        "draft_count": draft_count,
        "scheduled_count": scheduled_count,
        "published_count": published_count,
        "failed_count": failed_count,
        "accounts": accounts,
        "templates": templates,
        "rules": rules,
        "posts": posts,
    }

    return render(request, "socialmedia/index.html", context)


@login_required
def export_posts_csv(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()

    with scope(event=event_obj):
        posts = SocialPost.objects.filter(event=event_obj)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="social_posts_{event_obj.slug}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "Event Name",
            "Organizer Name",
            "Platform/Channel",
            "Post Text",
            "Status",
            "Scheduled Date Time",
        ])
        for post in posts:
            writer.writerow([
                event_obj.name,
                event_obj.organizer.name,
                post.account.provider if post.account else "",
                post.text,
                post.status,
                post.scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
                if post.scheduled_time
                else "",
            ])
        return response


@login_required
def account_create(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        provider = request.POST.get("provider")
        account_name = request.POST.get("account_name")
        with scope(event=event_obj):
            SocialMediaAccount.objects.create(
                event=event_obj,
                provider=provider,
                account_name=account_name,
                credentials="{}",
                is_active=True,
            )
        messages.success(request, "Social media account added successfully.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#accounts"
    )


@login_required
def account_delete(request, organizer, event, pk):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        with scope(event=event_obj):
            account = get_object_or_404(SocialMediaAccount, pk=pk, event=event_obj)
            account.delete()
        messages.success(request, "Social media account deleted.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#accounts"
    )


@login_required
def template_create(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        name = request.POST.get("name")
        template_text = request.POST.get("template_text")
        with scope(event=event_obj):
            PostTemplate.objects.create(
                event=event_obj,
                name=name,
                template_text=template_text,
                is_active=True,
            )
        messages.success(request, "Template created successfully.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#templates"
    )


@login_required
def template_delete(request, organizer, event, pk):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        with scope(event=event_obj):
            template = get_object_or_404(PostTemplate, pk=pk, event=event_obj)
            template.delete()
        messages.success(request, "Template deleted.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#templates"
    )


@login_required
def rule_create(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        template_id = request.POST.get("template")
        trigger_type = request.POST.get("trigger_type")
        offset_minutes = request.POST.get("offset_minutes")
        with scope(event=event_obj):
            template = get_object_or_404(PostTemplate, pk=template_id, event=event_obj)
            ScheduleRule.objects.create(
                event=event_obj,
                template=template,
                trigger_type=trigger_type,
                offset_minutes=int(offset_minutes),
                is_active=True,
            )
        messages.success(request, "Schedule rule created successfully.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#rules"
    )


@login_required
def rule_delete(request, organizer, event, pk):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        with scope(event=event_obj):
            rule = get_object_or_404(ScheduleRule, pk=pk, event=event_obj)
            rule.delete()
        messages.success(request, "Schedule rule deleted.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#rules"
    )


@login_required
def post_create(request, organizer, event):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        account_id = request.POST.get("account")
        text = request.POST.get("text")
        status = request.POST.get("status", "draft")
        with scope(event=event_obj):
            account = get_object_or_404(SocialMediaAccount, pk=account_id, event=event_obj)
            SocialPost.objects.create(
                event=event_obj,
                account=account,
                text=text,
                status=status,
            )
        messages.success(request, "Social post announcement created successfully.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#posts"
    )


@login_required
def post_delete(request, organizer, event, pk):
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    if not request.user.has_event_permission(
        event_obj.organizer,
        event_obj,
        "can_change_event_settings",
        request=request,
    ):
        raise PermissionDenied()
    if request.method == "POST":
        with scope(event=event_obj):
            post = get_object_or_404(SocialPost, pk=pk, event=event_obj)
            post.delete()
        messages.success(request, "Social post announcement deleted.")
    return redirect(
        reverse(
            "plugins:socialmedia:index",
            kwargs={"organizer": organizer, "event": event},
        )
        + "#posts"
    )
