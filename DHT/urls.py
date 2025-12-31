from django.urls import path
from django.shortcuts import redirect
from . import views, api

# redirection auto vers login
def go_login(request):
    return redirect("login")

urlpatterns = [
    path("", go_login, name="home"),  # 🔥 Première page = login

    # Auth pages
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Data APIs
    path("latest/", views.latest_json, name="latest_json"),
    path("api/", api.DList.as_view(), name="json"),
    path("api/post/", api.DhtViews.as_view(), name="json_post"),

    # Historique
    path("temperature/history/", views.temperature_history, name="temperature_history"),
    path("temperature/history/csv/", views.temperature_history_csv, name="temperature_history_csv"),

    path("humidity/history/", views.humidity_history, name="humidity_history"),
    path("humidity/history/csv/", views.humidity_history_csv, name="humidity_history_csv"),
]
