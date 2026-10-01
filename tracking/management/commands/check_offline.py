from django.core.management.base import BaseCommand
from django.utils import timezone
from fleet.models import Bus
from tracking.models import BusLocation, OfflineEvent
import datetime

class Command(BaseCommand):
    help = 'Checks for buses that have stopped sending GPS updates'

    def handle(self, *args, **options):
        threshold = timezone.now() - datetime.timedelta(minutes=5)
        active_buses = Bus.objects.filter(is_active=True)
        
        for bus in active_buses:
            last_ping = BusLocation.objects.filter(bus=bus).order_by('-timestamp').first()
            
            if last_ping:
                if last_ping.timestamp < threshold:
                    # Bus is offline
                    self.stdout.write(self.style.WARNING(f"Bus {bus.bus_number} is offline. Last saw at {last_ping.timestamp}"))
                    OfflineEvent.objects.get_or_create(bus=bus, resolved_at__isnull=True, defaults={'detected_at': timezone.now()})
                else:
                    # Bus is online, resolve any open offline events
                    OfflineEvent.objects.filter(bus=bus, resolved_at__isnull=True).update(resolved_at=timezone.now())
            else:
                self.stdout.write(self.style.WARNING(f"Bus {bus.bus_number} has no GPS history."))
