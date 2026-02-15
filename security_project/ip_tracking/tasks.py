from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP
import logging

logger = logging.getLogger(__name__)

@shared_task
def detect_suspicious_ips():
    """
    Hourly task to detect suspicious IPs based on:
    - More than 100 requests in the last hour
    - Access to sensitive paths (/admin/, /login/)
    """
    
    one_hour_ago = timezone.now() - timedelta(hours=1)
    sensitive_paths = ['/admin/', '/login/', '/dashboard/']
    
    suspicious_count = 0
    
    # 1. Detect IPs with high request volume (>100 requests/hour)
    high_volume_ips = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago
    ).values('ip_address').annotate(
        request_count=Count('id')
    ).filter(request_count__gt=100)
    
    for ip_data in high_volume_ips:
        ip_address = ip_data['ip_address']
        count = ip_data['request_count']
        
        # Create or update suspicious IP record
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': f"High request volume: {count} requests in the last hour",
                'detected_at': timezone.now()
            }
        )
        
        if not created:
            # Update existing record
            suspicious_ip.reason = f"High request volume: {count} requests in the last hour"
            suspicious_ip.detected_at = timezone.now()
            suspicious_ip.is_resolved = False
            suspicious_ip.save()
        
        suspicious_count += 1
        logger.warning(f"Suspicious IP detected: {ip_address} - {count} requests/hour")
    
    # 2. Detect IPs accessing sensitive paths
    sensitive_access_ips = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=sensitive_paths
    ).values('ip_address').annotate(
        access_count=Count('id')
    ).filter(access_count__gte=5)  # At least 5 accesses to sensitive paths
    
    for ip_data in sensitive_access_ips:
        ip_address = ip_data['ip_address']
        count = ip_data['access_count']
        
        # Create or update suspicious IP record
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': f"Suspicious activity: accessed sensitive paths {count} times",
                'detected_at': timezone.now()
            }
        )
        
        if not created:
            # Update existing record
            suspicious_ip.reason = f"Suspicious activity: accessed sensitive paths {count} times"
            suspicious_ip.detected_at = timezone.now()
            suspicious_ip.is_resolved = False
            suspicious_ip.save()
        
        suspicious_count += 1
        logger.warning(f"Suspicious IP detected: {ip_address} - {count} sensitive path accesses")
    
    # 3. Detect IPs that are both high volume and accessing sensitive paths
    # This is already covered by the above queries, but we can add a combined check
    
    result_message = f"Anomaly detection complete. Found {suspicious_count} suspicious IPs."
    logger.info(result_message)
    
    return result_message

@shared_task
def cleanup_old_logs():
    """
    Optional: Clean up old request logs (older than 7 days)
    """
    seven_days_ago = timezone.now() - timedelta(days=7)
    deleted_count = RequestLog.objects.filter(timestamp__lt=seven_days_ago).delete()[0]
    logger.info(f"Cleaned up {deleted_count} old request logs")
    return f"Cleaned up {deleted_count} old logs"