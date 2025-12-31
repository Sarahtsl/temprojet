from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Dht11
import json
import csv


# ===================== AUTH =====================

def register_view(request):
    """
    Inscription d'un nouvel utilisateur.
    Après inscription, on le connecte et on l'envoie vers le dashboard.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connexion directe après inscription
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    """
    Page de connexion.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    """
    Déconnexion puis redirection vers la page de login.
    """
    logout(request)
    return redirect("login")


# ===================== DASHBOARD =====================

@login_required(login_url="login")
def dashboard(request):
    """
    Page principale avec les cartes Température / Humidité.
    """
    return render(request, "dashboard.html")


# ===================== /latest/ (public) =====================

def latest_json(request):
    """
    Renvoie la dernière mesure en JSON.
    (Tu peux la laisser publique, utile pour le dashboard ou une autre app.)
    """
    last = Dht11.objects.order_by("-created_at").first()
    if not last:
        return JsonResponse({"temp": None, "hum": None, "date": None})

    return JsonResponse(
        {
            "temp": float(last.temperature),
            "hum": float(last.humidity),
            "date": last.created_at.isoformat(),
        }
    )


# ===================== HISTORIQUE TEMPÉRATURE =====================

@login_required(login_url="login")
def temperature_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    labels = [m.created_at.strftime("%Y-%m-%d %H:%M") for m in qs]
    temps = [float(m.temperature) for m in qs]
    hums = [float(m.humidity) for m in qs]

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "temperature_history.html", context)


@login_required(login_url="login")
def temperature_history_csv(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="temperature_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Capteur", "Température (°C)", "Humidité (%)"])
    for m in qs:
        writer.writerow([m.created_at, m.sensor_id, m.temperature, m.humidity])

    return response


# ===================== HISTORIQUE HUMIDITÉ =====================

@login_required(login_url="login")
def humidity_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    labels = [m.created_at.isoformat() for m in qs]
    temps = [float(m.temperature) for m in qs]
    hums = [float(m.humidity) for m in qs]

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "humidity_history.html", context)


@login_required(login_url="login")
def humidity_history_csv(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="humidity_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Capteur", "Température (°C)", "Humidité (%)"])
    for m in qs:
        writer.writerow([m.created_at, m.sensor_id, m.temperature, m.humidity])

    return response
