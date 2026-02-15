from django.db import models

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        location = f" - {self.city}, {self.country}" if self.city and self.country else ""
        return f"{self.ip_address}{location} - {self.timestamp}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.ip_address

# NEW: Add SuspiciousIP model for Task 4
class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField(db_index=True)
    reason = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name_plural = "Suspicious IPs"
    
    def __str__(self):
        return f"{self.ip_address} - {self.detected_at}"