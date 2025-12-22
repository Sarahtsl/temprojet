from django.db import models

class Dht11(models.Model):
    sensor_id = models.IntegerField(default=1)
    temperature = models.FloatField()
    humidity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Capteur {self.sensor_id} - {self.temperature}°C / {self.humidity}%"
