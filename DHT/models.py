from django.db import models
from django.utils import timezone

class Dht11(models.Model):
    sensor_id = models.IntegerField(default=1)
    temperature = models.FloatField()
    humidity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Capteur {self.sensor_id} - {self.temperature}°C / {self.humidity}%"

class Incident(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    counter = models.IntegerField(default=0)
    max_temperature = models.FloatField()

    # opérateurs
    op1_ack = models.BooleanField(default=False)
    op1_comment = models.TextField(blank=True)

    op2_ack = models.BooleanField(default=False)
    op2_comment = models.TextField(blank=True)

    op3_ack = models.BooleanField(default=False)
    op3_comment = models.TextField(blank=True)

    def __str__(self):
        return f"Incident {self.start_time.strftime('%Y-%m-%d %H:%M')}"