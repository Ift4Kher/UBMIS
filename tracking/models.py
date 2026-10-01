from django.db import models
from fleet.models import Bus

class BusLocation(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bus.bus_number} at {self.timestamp}"

class OfflineEvent(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
