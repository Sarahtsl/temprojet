from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("latest/", views.latest_json, name="latest_json"),

    path("api/", api.DList.as_view(), name="json"),
    path("api/post", api.DhtViews.as_view(), name="json_post"),

    path("temperature/history/", views.temperature_history, name="temperature_history"),
    path(
        "temperature/history/csv/",
        views.temperature_history_csv,
        name="temperature_history_csv",
    ),

    path("humidity/history/", views.humidity_history, name="humidity_history"),
    path(
        "humidity/history/csv/",
        views.humidity_history_csv,
        name="humidity_history_csv",
    ),
]
