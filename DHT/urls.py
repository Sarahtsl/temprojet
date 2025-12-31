from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ====================== PAGES ======================
    path("", views.dashboard, name="dashboard"),

    # ======================= API ======================
    path("latest/", views.latest_json, name="latest_json"),
    path("api/post/", views.esp8266_api, name="esp8266_api"),  # <-- ESP8266

    # ================== TEMPERATURE ===================
    path("temperature/history/", views.temperature_history, name="temperature_history"),
    path("temperature/history/csv/", views.temperature_history_csv, name="temperature_history_csv"),

    # =================== HUMIDITE =====================
    path("humidity/history/", views.humidity_history, name="humidity_history"),
    path("humidity/history/csv/", views.humidity_history_csv, name="humidity_history_csv"),

    # ======================= AUTH =====================
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register_view, name="register"),
]
