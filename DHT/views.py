from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from .models import Dht11
import json
import csv


# ===================== AUTH (INSCRIPTION) =====================
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connexion مباشرة بعد التسجيل
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


# ===================== DASHBOARD =====================
@login_required(login_url="login")
def dashboard(request):
    return render(request, "dashboard.html")


# ===================== /latest/ (tu peux le laisser public) =====================
def latest_json(request):
    last = Dht11.objects.order_by("-created_at").first()
    if not last:
        return JsonResponse({"temp": None, "hum": None, "date": None})

    return JsonResponse({
        "temp": float(last.temperature),
        "hum": float(last.humidity),
        "date": last.created_at.isoformat(),
    })


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

@csrf_exempt
def esp8266_api(request):
    # ======= POST : appelé par l'ESP8266 =======
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON invalide"}, status=400)

        temperature = data.get("temperature")
        humidity = data.get("humidity")
        sensor_id = data.get("sensor_id", 1)  # 1 par défaut

        if temperature is None or humidity is None:
            return JsonResponse({"error": "champs manquants"}, status=400)

        # Enregistrement dans la BD
        mesure = Dht11.objects.create(
            temperature=temperature,
            humidity=humidity,
            sensor_id=sensor_id,
        )

        return JsonResponse({
            "status": "ok",
            "temperature": float(mesure.temperature),
            "humidity": float(mesure.humidity),
            "date": mesure.created_at.isoformat(),
            "sensor_id": mesure.sensor_id,
        }, status=201)

    # ======= GET : retourner la DERNIERE valeur =======
    elif request.method == "GET":
        last = Dht11.objects.order_by("-created_at").first()
        if not last:
            return JsonResponse({
                "temperature": None,
                "humidity": None,
                "date": None,
                "sensor_id": None,
            })

        return JsonResponse({
            "temperature": float(last.temperature),
            "humidity": float(last.humidity),
            "date": last.created_at.isoformat(),
            "sensor_id": last.sensor_id,
        })

    # ======= Autres méthodes non supportées =======
    return JsonResponse({"error": "Méthode non supportée"}, status=405)
