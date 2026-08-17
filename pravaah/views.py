from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import connection
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from .models import Event, Member, Movie, Journal


def home(request):
    return render(request, 'index.html')


def events_list(request):
    events = Event.objects.all()
    return render(request, 'events/list.html', {'events': events})


def event_detail(request, slug):
    event = get_object_or_404(
        Event.objects.prefetch_related('gallery'),
        slug=slug
    )
    return render(request, 'events/detail.html', {'event': event})


def team_list(request):
    position_order = [
        "President",
        "Vice President",
        "Treasurer",
        "Secretary",
        "Joint Secretary",
        "Executive Member",
        "Member",
    ]

    whens = [
        When(position__iexact=pos, then=Value(idx))
        for idx, pos in enumerate(position_order, start=1)
    ]

    members = list(
        Member.objects.annotate(
            rank=Case(*whens, default=Value(99), output_field=IntegerField())
        ).order_by("rank", "id")
    )

    presidents = [m for m in members if m.rank == 1]
    vice_presidents = [m for m in members if m.rank == 2]
    leadership = [m for m in members if m.rank in (3, 4, 5)]
    executive_members = [m for m in members if m.rank == 6]
    general_members = [m for m in members if m.rank in (7, 99)]

    context = {
        "members": members,
        "presidents": presidents,
        "vice_presidents": vice_presidents,
        "leadership": leadership,
        "executive_members": executive_members,
        "general_members": general_members,
    }
    return render(request, "team/list.html", context)


def films_list(request):
    movies = Movie.objects.all().order_by("-release_date")
    return render(request, "films/list.html", {"movies": movies})


def journal_list(request):
    articles = (
        Journal.objects.filter(
            published_at__isnull=False, published_at__lte=timezone.now()
        )
        .select_related("author")
        .order_by("-published_at")
    )
    return render(request, "journal/list.html", {"articles": articles})


def journal_detail(request, slug):
    article = get_object_or_404(
        Journal.objects.select_related("author"),
        slug=slug,
        published_at__isnull=False,
        published_at__lte=timezone.now(),
    )
    return render(request, "journal/detail.html", {"article": article})


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "database": "unhealthy", "detail": str(exc)},
            status=503,
        )
