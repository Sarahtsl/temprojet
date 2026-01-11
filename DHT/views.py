
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404
from .models import Dht11, Incident

import json
import csv


# ===================== AUTH =====================

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
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
    logout(request)
    return redirect("login")


# ===================== DASHBOARD =====================

@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


# ===================== /latest/ =====================
# Donnée brute capteur (utilisée par le JS)

def latest_json(request):
    last = Dht11.objects.order_by("-created_at").first()

    if not last:
        return JsonResponse({
            "temp": None,
            "hum": None,
            "date": None
        })

    return JsonResponse({
        "temp": float(last.temperature),
        "hum": float(last.humidity),
        "date": last.created_at.isoformat()
    })


# ===================== INCIDENT STATUS =====================

def incident_status(request):
    incident = Incident.objects.filter(end_time__isnull=True).last()

    if not incident:
        return JsonResponse({"active": False})

    return JsonResponse({
        "active": True,
        "counter": incident.counter,
        "max_temperature": incident.max_temperature,
        "start_time": incident.start_time.isoformat()
    })


# ===================== INCIDENT UPDATE (OPÉRATEURS) =====================

@csrf_exempt
def incident_update(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    op = data.get("op")
    ack = data.get("ack")
    comment = data.get("comment")

    incident = Incident.objects.filter(end_time__isnull=True).last()
    if not incident:
        return JsonResponse({"error": "no active incident"}, status=400)

    if op == 1:
        incident.op1_ack = ack
        incident.op1_comment = comment
    elif op == 2:
        incident.op2_ack = ack
        incident.op2_comment = comment
    elif op == 3:
        incident.op3_ack = ack
        incident.op3_comment = comment

    incident.save()
    return JsonResponse({"status": "ok"})


# ===================== INCIDENT LOGIQUE (ÉTAPE 3) =====================
# Appelée automatiquement à chaque nouvelle mesure

def process_incident(temperature):
    incident = Incident.objects.filter(end_time__isnull=True).last()
    is_alert = temperature < 2 or temperature > 8

    if is_alert:
        if not incident:
            Incident.objects.create(
                start_time=timezone.now(),
                counter=1,
                max_temperature=temperature
            )
        else:
            incident.counter += 1
            incident.max_temperature = max(incident.max_temperature, temperature)
            incident.save()
    else:
        if incident:
            incident.end_time = timezone.now()
            incident.save()


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

    return render(request, "temperature_history.html", {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date": end_date or "",
    })


@login_required(login_url="login")
def temperature_history_csv(request):
    qs = Dht11.objects.all().order_by("created_at")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="temperature_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Capteur", "Température", "Humidité"])
    for m in qs:
        writer.writerow([m.created_at, m.sensor_id, m.temperature, m.humidity])

    return response


# ===================== HISTORIQUE HUMIDITÉ =====================

@login_required(login_url="login")
def humidity_history(request):
    qs = Dht11.objects.all().order_by("created_at")

    labels = [m.created_at.strftime("%Y-%m-%d %H:%M") for m in qs]
    temps = [float(m.temperature) for m in qs]
    hums = [float(m.humidity) for m in qs]

    return render(request, "humidity_history.html", {
        "labels": mark_safe(json.dumps(labels)),
        "temps": mark_safe(json.dumps(temps)),
        "hums": mark_safe(json.dumps(hums)),
    })


@login_required(login_url="login")
def humidity_history_csv(request):
    qs = Dht11.objects.all().order_by("created_at")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="humidity_history.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Capteur", "Température", "Humidité"])
    for m in qs:
        writer.writerow([m.created_at, m.sensor_id, m.temperature, m.humidity])

    return response

def incident_archive(request):
    # Récupérer tous les incidents, qu'ils soient clôturés ou actifs
    incidents = Incident.objects.all().order_by("-start_time")

    # Préparer un champ pour l'affichage de end_time
    for inc in incidents:
        if inc.end_time is None:
            # Si l'incident est actif, afficher la date/heure actuelle
            inc.end_time_display = timezone.localtime(timezone.now())
        else:
            inc.end_time_display = inc.end_time

    return render(request, "incident_archive.html", {
        "incidents": incidents
    })

@login_required(login_url="login")
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    return render(request, "incident_detail.html", {
        "incident": incident
    })

def post_data_view(request):
    return render(request, "post_data.html")