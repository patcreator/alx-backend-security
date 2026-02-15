import logging
from django.utils import timezone
from .models import RequestLog

# This sets up logging so we can see what's happening
logger = logging.getLogger(__name__)

class IPLoggingMiddleware:
    def __init__(self, get_response):
        # This runs once when the server starts
        self.get_response = get_response
        print("IP Logging Middleware initialized!")
    
    def __call__(self, request):
        # This runs for EVERY request
        
        # Get the visitor's IP address
        # Sometimes the real IP is in X-Forwarded-For (if behind a proxy)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list (the real visitor)
            ip_address = x_forwarded_for.split(',')[0]
        else:
            # Direct connection - get IP directly
            ip_address = request.META.get('REMOTE_ADDR')
        
        print(f"Visitor IP: {ip_address} - Path: {request.path}")
        
        # Save to database
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path
        )
        
        # Log to console
        logger.info(f"IP: {ip_address} - Path: {request.path}")
        
        # Continue with the normal request
        response = self.get_response(request)
        
        return response