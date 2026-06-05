from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def index(request, organizer, event):
    return HttpResponse(f"Social Media Works for event: {event}")


@login_required
def global_index(request):
    return HttpResponse("Social Media Global Dashboard Works")


