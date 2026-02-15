from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Block an IP address from accessing the site'
    
    def add_arguments(self, parser):
        # This tells Django that we need an IP address argument
        parser.add_argument('ip_address', type=str, help='The IP address to block')
    
    def handle(self, *args, **options):
        ip_address = options['ip_address']
        
        try:
            # Try to create a new blocked IP entry
            blocked_ip, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully blocked IP: {ip_address}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'IP {ip_address} was already blocked')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error blocking IP {ip_address}: {str(e)}')
            )