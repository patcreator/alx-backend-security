from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@never_cache
@ratelimit(key='ip', rate='5/m', method='ALL', block=True)
def login_view(request):
    """
    Login view with rate limiting:
    - 5 requests per minute for anonymous users
    - Returns 403 if rate limit exceeded
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logger.info(f"Successful login from IP: {request.META.get('REMOTE_ADDR')}")
            return redirect('home')
        else:
            logger.warning(f"Failed login attempt from IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'ip_tracking/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'ip_tracking/login.html')

@login_required
@ratelimit(key='user', rate='10/m', method='ALL', block=True)
def dashboard_view(request):
    """
    Dashboard view for authenticated users:
    - 10 requests per minute
    - Requires login
    """
    return render(request, 'ip_tracking/dashboard.html')

def home_view(request):
    """Public home page"""
    return render(request, 'ip_tracking/home.html')

def rate_limited_view(request):
    """View that demonstrates rate limiting"""
    return HttpResponse("This is a rate-limited endpoint")

# Optional: Custom handler for rate limit exceeded
def rate_limit_exceeded(request, exception):
    return render(request, 'ip_tracking/rate_limit_exceeded.html', status=429)