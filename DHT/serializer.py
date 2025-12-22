from rest_framework import serializers
from .models import Dht11

class Dht11Serializer(serializers.ModelSerializer):
    class Meta:
        model = Dht11
        fields = ["id", "sensor_id", "temperature", "humidity", "created_at"]
