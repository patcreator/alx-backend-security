import logging
import hashlib
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django_ip_geolocation.decorators import with_ip_geolocation
from .models import RequestLog, BlockedIP

logger = logging.getLogger(__name__)

# Initialize the IP Geolocation API with your key
try:
    ipgeolocation_api = with_ip_geolocation(api_key=settings.IPGEOLOCATION_API_KEY)
    print("✅ IPGeolocation API initialized successfully!")
except AttributeError:
    logger.error("❌ IPGEOLOCATION_API_KEY not found in settings")
    ipgeolocation_api = None
except Exception as e:
    logger.error(f"❌ Error initializing IPGeolocation: {str(e)}")
    ipgeolocation_api = None

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("🚀 IP Logging Middleware initialized with django-ip-geolocation!")
    
    def get_geolocation(self, ip_address):
        """
        Get geolocation data for an IP address using django-ipgeolocation
        Cache results for 24 hours to avoid hitting API limits
        """
        # Skip geolocation for local/private IPs
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {'country': 'Local', 'city': 'Local'}
        
        # Create a cache key unique to this IP
        cache_key = f"geo_{hashlib.md5(ip_address.encode()).hexdigest()}"
        
        # Try to get from cache first
        geo_data = cache.get(cache_key)
        
        if not geo_data and ipgeolocation_api:
            try:
                print(f"🌍 Fetching geolocation for IP: {ip_address}")
                
                # Get location from API
                location = ipgeolocation_api.get_location(ip_address)
                
                geo_data = {
                    'country': location.get('country_name', 'Unknown'),
                    'city': location.get('city', 'Unknown'),
                }
                
                # Cache for 24 hours (86400 seconds)
                cache.set(cache_key, geo_data, timeout=86400)
                print(f"✅ Geolocation cached: {geo_data['city']}, {geo_data['country']}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching geolocation for {ip_address}: {str(e)}")
                geo_data = {'country': 'Error', 'city': 'Error'}
        
        return geo_data or {'country': 'Unknown', 'city': 'Unknown'}
    
    def __call__(self, request):
        # Get the visitor's IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Check if this IP is blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            print(f"🚫 BLOCKED request from IP: {ip_address}")
            return HttpResponseForbidden("Your IP address has been blocked. Access denied.")
        
        # Get geolocation data
        geo_data = self.get_geolocation(ip_address)
        
        print(f"👤 Visitor: {ip_address} - 📍 {geo_data['city']}, {geo_data['country']} - 📁 {request.path}")
        
        # Save to database with geolocation
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            country=geo_data['country'],
            city=geo_data['city']
        )
        
        response = self.get_response(request)
        return response