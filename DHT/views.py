from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from .models import Dht11
import json
import csv


# ---------- DASHBOARD ----------
def dashboard(request):
    # page avec les 2 cartes (temp & humidité)
    return render(request, "dashboard.html")


# ---------- /latest/ ----------
def latest_json(request):
    last = Dht11.objects.order_by("-created_at").first()
    if not last:
        return JsonResponse({"temp": None, "hum": None, "date": None})

    return JsonResponse({
        "temp": float(last.temperature),
        "hum": float(last.humidity),
        "date": last.created_at.isoformat(),
    })



# ---------- HISTORIQUE TEMPÉRATURE ----------
def temperature_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    labels = [m.created_at.strftime("%Y-%m-%d %H:%M") for m in qs]
    temps  = [float(m.temperature) for m in qs]
    hums   = [float(m.humidity) for m in qs]

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps":  mark_safe(json.dumps(temps)),
        "hums":   mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date":   end_date or "",
    }
    return render(request, "temperature_history.html", context)


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

# ---------- HISTORIQUE HUMIDITÉ ----------
def humidity_history(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = Dht11.objects.all().order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    # ⚠️ important : ISO 8601 pour l'axe temps
    labels = [m.created_at.isoformat() for m in qs]
    temps  = [float(m.temperature) for m in qs]
    hums   = [float(m.humidity) for m in qs]

    from django.utils.safestring import mark_safe
    import json

    context = {
        "labels": mark_safe(json.dumps(labels)),
        "temps":  mark_safe(json.dumps(temps)),
        "hums":   mark_safe(json.dumps(hums)),
        "start_date": start_date or "",
        "end_date":   end_date or "",
    }
    return render(request, "humidity_history.html", context)



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
